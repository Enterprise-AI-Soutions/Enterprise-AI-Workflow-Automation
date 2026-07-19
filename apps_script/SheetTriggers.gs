/**
 * SheetTriggers.gs — Event-driven automation triggered by Sheet changes.
 *
 * Triggers:
 *   onEdit(e)         — Detect new rows in designated input columns and process them
 *   onFormSubmit(e)   — Process Google Form submissions with AI
 *   syncCalendarEvents() — Pull upcoming calendar events into a sheet
 *   showAiFillDialog()   — Prompt user to AI-generate data and write to active sheet
 */

// ── On-Edit Trigger ───────────────────────────────────────────────────────────

/**
 * Fires every time a cell is edited. 
 * Watches column A of the "Input" sheet for new text entries and 
 * automatically classifies them, writing the result to column B.
 *
 * @param {GoogleAppsScript.Events.SheetsOnEdit} e
 */
function onEdit(e) {
  if (!e) return;

  const sheet = e.range.getSheet();
  const sheetName = sheet.getName();
  const col = e.range.getColumn();
  const row = e.range.getRow();
  const value = e.value;

  // Only act on the "Input" sheet, column A, rows 2+
  if (sheetName !== 'Input' || col !== 1 || row < 2 || !value || value.length < 5) return;

  // Mark as processing
  sheet.getRange(row, 2).setValue('⏳ Processing...');

  // Classify in background (must be synchronous in onEdit)
  try {
    const resp = apiPost('/ai/classify', {
      text: value,
      categories: ['Sales Inquiry', 'Support Request', 'Finance', 'HR', 'Engineering', 'Spam', 'Other'],
    });

    const category = resp.error ? 'Error' : (resp.category || 'Unknown');
    const confidence = resp.confidence ? ' (' + Math.round(resp.confidence * 100) + '%)' : '';

    sheet.getRange(row, 2).setValue(category + confidence);

    // Set background colour based on category
    const colours = {
      'Sales Inquiry': '#dbeafe',
      'Support Request': '#fef3c7',
      'Finance': '#d1fae5',
      'HR': '#ede9fe',
      'Engineering': '#e0f2fe',
      'Spam': '#fee2e2',
    };
    sheet.getRange(row, 1, 1, 2).setBackground(colours[category] || '#f8fafc');

    // Log timestamp
    sheet.getRange(row, 3).setValue(new Date().toLocaleString());

  } catch (err) {
    sheet.getRange(row, 2).setValue('❌ Error: ' + err.message);
  }
}

// ── Form Submit Handler ───────────────────────────────────────────────────────

/**
 * Processes a Google Form submission with Claude AI.
 * Extracts structured fields and logs the enriched record to the "CRM" sheet.
 *
 * Link this to your form's "On form submit" trigger.
 *
 * @param {GoogleAppsScript.Events.SheetsOnFormSubmit} e
 */
function onFormSubmit(e) {
  if (!e) return;

  const responses = e.namedValues; // { 'Question': ['Answer'], ... }
  const fullText = Object.entries(responses)
    .map(([q, a]) => `${q}: ${a.join(', ')}`)
    .join('\n');

  // Extract structured fields
  const extractResp = apiPost('/ai/extract', {
    text: fullText,
    fields: ['name', 'email', 'company', 'message', 'budget', 'urgency'],
  });

  // Classify intent
  const classifyResp = apiPost('/ai/classify', {
    text: fullText,
    categories: ['Sales Inquiry', 'Support Request', 'Partnership', 'Job Application', 'Other'],
  });

  // Write to CRM sheet
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let crmSheet = ss.getSheetByName('CRM');
  if (!crmSheet) {
    crmSheet = ss.insertSheet('CRM');
    const headers = ['Submitted At', 'Name', 'Email', 'Company', 'Intent', 'Confidence', 'Message', 'Budget', 'Urgency'];
    crmSheet.appendRow(headers);
    crmSheet.getRange(1, 1, 1, headers.length).setFontWeight('bold').setBackground('#1a56db').setFontColor('#ffffff');
    crmSheet.setFrozenRows(1);
  }

  const fields = extractResp.fields || {};
  crmSheet.appendRow([
    new Date().toISOString(),
    fields.name || '',
    fields.email || '',
    fields.company || '',
    classifyResp.category || 'Unknown',
    classifyResp.confidence ? Math.round(classifyResp.confidence * 100) + '%' : '?',
    fields.message || '',
    fields.budget || '',
    fields.urgency || '',
  ]);

  Logger.log('Form submission processed: %s', JSON.stringify(fields));
  logToSheet('onFormSubmit', 'success', { category: classifyResp.category });
}

// ── Calendar Sync ─────────────────────────────────────────────────────────────

/**
 * Fetch upcoming Google Calendar events via the FastAPI backend
 * and write them to a "Calendar" sheet.
 *
 * Called by: time-based trigger (daily at 8am) or menu item.
 */
function syncCalendarEvents() {
  const resp = apiGet('/google/calendar/events', { max_results: 20 });

  if (resp.error || !resp.events) {
    Logger.log('Could not fetch calendar events: %s', JSON.stringify(resp));
    return;
  }

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName('Calendar');
  if (!sheet) {
    sheet = ss.insertSheet('Calendar');
  } else {
    sheet.clearContents();
  }

  const headers = ['Event ID', 'Title', 'Start', 'End', 'Attendees', 'Last Synced'];
  sheet.appendRow(headers);
  sheet.getRange(1, 1, 1, headers.length).setFontWeight('bold').setBackground('#1a56db').setFontColor('#ffffff');
  sheet.setFrozenRows(1);

  const now = new Date().toISOString();
  resp.events.forEach(event => {
    sheet.appendRow([
      event.id || '',
      event.summary || '(no title)',
      event.start || '',
      event.end || '',
      (event.attendees || []).join(', '),
      now,
    ]);
  });

  sheet.autoResizeColumns(1, headers.length);
  logToSheet('syncCalendarEvents', 'success', { count: resp.events.length });
  toast(`Synced ${resp.events.length} calendar event(s) → Calendar sheet`);
}

// ── AI Fill Dialog ────────────────────────────────────────────────────────────

/**
 * Show a prompt for the user to describe data to AI-generate into the active sheet.
 */
function showAiFillDialog() {
  const ui = SpreadsheetApp.getUi();

  const headersResp = ui.prompt(
    '✨ AI Fill — Column Headers',
    'Enter comma-separated column headers (e.g. Name, Email, Company, Revenue):',
    ui.ButtonSet.OK_CANCEL
  );
  if (headersResp.getSelectedButton() !== ui.Button.OK) return;

  const headers = headersResp.getResponseText().split(',').map(h => h.trim()).filter(Boolean);
  if (headers.length === 0) {
    ui.alert('No headers provided.');
    return;
  }

  const descResp = ui.prompt(
    '✨ AI Fill — Data Description',
    'Describe what data to generate (e.g. "SaaS company leads from the US tech industry"):',
    ui.ButtonSet.OK_CANCEL
  );
  if (descResp.getSelectedButton() !== ui.Button.OK) return;

  const rowsResp = ui.prompt(
    '✨ AI Fill — Row Count',
    'How many data rows to generate? (1–20):',
    ui.ButtonSet.OK_CANCEL
  );
  if (rowsResp.getSelectedButton() !== ui.Button.OK) return;

  const rows = Math.min(20, Math.max(1, parseInt(rowsResp.getResponseText(), 10) || 5));

  toast(`Generating ${rows} rows with AI...`);

  const spreadsheetId = SpreadsheetApp.getActiveSpreadsheet().getId();
  const resp = apiPost(`/google/sheets/${spreadsheetId}/ai-fill`, {
    headers: headers,
    prompt: descResp.getResponseText(),
    rows: rows,
  });

  if (resp.error) {
    ui.alert('❌ AI Fill failed: ' + (resp.message || 'Unknown error'));
    return;
  }

  // Reload the active sheet to show new data
  SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().getRange(1, 1).activate();
  toast(`✅ ${resp.rows_written} rows written by AI!`);
  logToSheet('aiFill', 'success', { rows: resp.rows_written, headers: headers });
}
