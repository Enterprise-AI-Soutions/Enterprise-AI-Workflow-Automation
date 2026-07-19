/**
 * EmailProcessor.gs — Process Gmail emails with Claude AI from Apps Script.
 *
 * Functions:
 *   processInboxEmails()   — Reads unread emails, classifies them with AI, logs to sheet
 *   classifySelectedRows() — Classify text in selected Sheets rows
 *   summariseSelectedCell()— Summarise the content of the selected cell
 */

// ── Gmail → Sheet pipeline ────────────────────────────────────────────────────

/**
 * Read up to 10 unread Gmail messages, classify each one using Claude AI,
 * and write the results to an "Email Triage" sheet.
 *
 * Called by: time-based trigger (every hour) or menu item.
 */
function processInboxEmails() {
  const resp = apiGet('/google/gmail/messages', { max_results: 10, query: 'is:unread' });

  if (resp.error || !resp.messages) {
    Logger.log('Could not fetch emails: %s', JSON.stringify(resp));
    return;
  }

  const messages = resp.messages;
  if (messages.length === 0) {
    toast('No unread emails found.');
    return;
  }

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName('Email Triage');
  if (!sheet) {
    sheet = ss.insertSheet('Email Triage');
    const headers = ['Message ID', 'Date', 'From', 'Subject', 'Snippet', 'AI Category', 'Confidence', 'Processed At'];
    sheet.appendRow(headers);
    sheet.getRange(1, 1, 1, headers.length).setFontWeight('bold').setBackground('#1a56db').setFontColor('#ffffff');
    sheet.setFrozenRows(1);
  }

  let processed = 0;
  messages.forEach(msg => {
    // Skip if already logged (check by message ID in column A)
    const existingIds = sheet.getRange('A:A').getValues().flat().map(String);
    if (existingIds.includes(msg.id)) return;

    // Classify with Claude AI
    const classifyResp = apiPost('/ai/classify', {
      text: `Subject: ${msg.subject || ''}\n\n${msg.snippet || ''}`,
      categories: ['Sales Inquiry', 'Support Request', 'Finance', 'HR', 'Engineering', 'Spam', 'Other'],
    });

    const category = classifyResp.category || 'Unknown';
    const confidence = classifyResp.confidence ? Math.round(classifyResp.confidence * 100) + '%' : '?';

    sheet.appendRow([
      msg.id,
      msg.date || '',
      msg.from || '',
      msg.subject || '(no subject)',
      msg.snippet || '',
      category,
      confidence,
      new Date().toISOString(),
    ]);

    // Colour-code by category
    const lastRow = sheet.getLastRow();
    const colours = {
      'Sales Inquiry': '#dbeafe',
      'Support Request': '#fef3c7',
      'Finance': '#d1fae5',
      'HR': '#ede9fe',
      'Engineering': '#e0f2fe',
      'Spam': '#fee2e2',
      'Other': '#f1f5f9',
    };
    const bg = colours[category] || '#f8fafc';
    sheet.getRange(lastRow, 1, 1, 8).setBackground(bg);

    processed++;
    Utilities.sleep(300); // Be kind to the API
  });

  sheet.autoResizeColumns(1, 8);
  logToSheet('processInboxEmails', 'success', { processed, total: messages.length });
  toast(`Processed ${processed} new email(s) → Email Triage sheet`);
}

// ── Classify selected Sheets rows ─────────────────────────────────────────────

/**
 * Classify the text in each selected row (reads column A or the selected column)
 * and writes the AI category into the next empty column.
 *
 * Select 1+ rows in your sheet, then run this from the menu.
 */
function classifySelectedRows() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const selection = sheet.getActiveRange();
  if (!selection) {
    SpreadsheetApp.getUi().alert('Please select one or more cells first.');
    return;
  }

  const values = selection.getValues();
  const categories = ['Sales Inquiry', 'Support Request', 'Finance', 'HR', 'Engineering', 'Spam', 'Other'];
  const results = [];

  toast(`Classifying ${values.length} row(s)...`);

  values.forEach(row => {
    const text = row.filter(Boolean).join(' ').trim();
    if (!text) {
      results.push(['—', '—']);
      return;
    }

    const resp = apiPost('/ai/classify', { text, categories });
    results.push([
      resp.error ? 'Error' : (resp.category || 'Unknown'),
      resp.error ? '' : (resp.confidence ? Math.round(resp.confidence * 100) + '%' : '?'),
    ]);
    Utilities.sleep(200);
  });

  // Write results to the right of the selection
  const outputCol = selection.getLastColumn() + 1;
  const outputRange = sheet.getRange(selection.getRow(), outputCol, results.length, 2);
  outputRange.setValues(results);

  // Header
  if (selection.getRow() > 1) {
    sheet.getRange(selection.getRow() - 1, outputCol, 1, 2).setValues([['AI Category', 'Confidence']]).setFontWeight('bold');
  }

  toast(`✅ Classified ${results.length} row(s)`);
  logToSheet('classifySelectedRows', 'success', { rows: results.length });
}

// ── Summarise selected cell ────────────────────────────────────────────────────

/**
 * Summarise the text in the currently active cell using Claude AI.
 * Opens an alert with the summary. Also writes it to the cell below.
 */
function summariseSelectedCell() {
  const cell = SpreadsheetApp.getActiveRange();
  const text = cell.getValue().toString().trim();

  if (!text || text.length < 20) {
    SpreadsheetApp.getUi().alert('Please select a cell with at least 20 characters of text.');
    return;
  }

  toast('Summarising with Claude AI...');

  const resp = apiPost('/ai/summarize', { text, max_words: 80 });

  if (resp.error) {
    SpreadsheetApp.getUi().alert('❌ Summarisation failed: ' + resp.message);
    return;
  }

  const summary = resp.summary || '(empty)';
  const isDemoMode = resp.demo_mode;

  // Write summary to the cell below
  const nextCell = cell.offset(1, 0);
  nextCell.setValue(summary);
  nextCell.setBackground('#fffbeb');
  nextCell.setNote('AI Summary' + (isDemoMode ? ' [demo mode]' : '') + ' — ' + new Date().toLocaleString());

  SpreadsheetApp.getUi().alert(
    '📄 AI Summary' + (isDemoMode ? ' (Demo Mode)' : ''),
    summary,
    SpreadsheetApp.getUi().ButtonSet.OK
  );

  logToSheet('summariseCell', 'success', { chars: text.length, demo: isDemoMode });
}
