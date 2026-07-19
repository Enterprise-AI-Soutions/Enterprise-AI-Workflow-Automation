/**
 * InvoiceProcessor.gs — Process invoice data from Google Sheets with Claude AI.
 *
 * Use Case:
 *   You have a Google Sheet where each row contains raw invoice text pasted 
 *   from a PDF or email. This script uses Claude AI to extract structured 
 *   fields (vendor, amount, due date, etc.) and writes them into adjacent columns.
 *
 * Setup:
 *   1. Create a sheet named "Invoices" with column A = "Raw Invoice Text"
 *   2. Paste raw invoice text into rows 2+ of column A
 *   3. Run `processAllInvoices()` from the ⚡ AI Workflows menu
 */

// ── Process all unprocessed invoices ──────────────────────────────────────────

/**
 * Iterate every row in the "Invoices" sheet and extract structured fields
 * from raw invoice text using Claude AI.
 */
function processAllInvoices() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName('Invoices');

  if (!sheet) {
    SpreadsheetApp.getUi().alert('No "Invoices" sheet found. Create one with raw invoice text in column A.');
    return;
  }

  const lastRow = sheet.getLastRow();
  if (lastRow < 2) {
    SpreadsheetApp.getUi().alert('No invoice data found. Add raw invoice text in column A starting at row 2.');
    return;
  }

  // Ensure header row
  const expectedHeaders = [
    'Raw Invoice Text', 'Invoice #', 'Vendor', 'Amount', 'Due Date',
    'Line Items', 'AI Confidence', 'Status', 'Processed At'
  ];
  sheet.getRange(1, 1, 1, expectedHeaders.length).setValues([expectedHeaders])
    .setFontWeight('bold')
    .setBackground('#1a56db')
    .setFontColor('#ffffff');
  sheet.setFrozenRows(1);

  const rawTexts = sheet.getRange(2, 1, lastRow - 1, 1).getValues();
  let processed = 0;
  let skipped = 0;

  rawTexts.forEach((row, i) => {
    const text = row[0] ? row[0].toString().trim() : '';
    const sheetRow = i + 2;

    // Skip empty or already processed
    if (!text || text.length < 20) { skipped++; return; }
    const existingStatus = sheet.getRange(sheetRow, 8).getValue();
    if (existingStatus === 'done') { skipped++; return; }

    sheet.getRange(sheetRow, 8).setValue('⏳ Processing...');

    const resp = apiPost('/ai/extract', {
      text,
      fields: ['invoice_number', 'vendor', 'amount', 'due_date', 'line_items'],
    });

    if (resp.error) {
      sheet.getRange(sheetRow, 8).setValue('❌ Error');
      Logger.log('Invoice extraction error at row %d: %s', sheetRow, resp.message);
      return;
    }

    const f = resp.fields || {};
    const confidence = resp.confidence ? Math.round(resp.confidence * 100) + '%' : '?';

    sheet.getRange(sheetRow, 2, 1, 8).setValues([[
      f.invoice_number || '',
      f.vendor || '',
      f.amount || '',
      f.due_date || '',
      Array.isArray(f.line_items) ? f.line_items.join('; ') : (f.line_items || ''),
      confidence,
      'done',
      new Date().toISOString(),
    ]]);

    // Colour-code confidence
    const confVal = resp.confidence || 0;
    const bg = confVal >= 0.8 ? '#d1fae5' : confVal >= 0.5 ? '#fef3c7' : '#fee2e2';
    sheet.getRange(sheetRow, 1, 1, 8).setBackground(bg);

    processed++;
    Utilities.sleep(400); // Rate-limit API calls
  });

  sheet.autoResizeColumns(1, 9);
  logToSheet('processAllInvoices', 'success', { processed, skipped });
  toast(`✅ Processed ${processed} invoice(s) (${skipped} skipped)`);
}

// ── Log new invoice to Airtable ───────────────────────────────────────────────

/**
 * Push all "done" invoices from the Invoices sheet to Airtable.
 * Requires AIRTABLE_BASE_ID and table "Invoices" to be configured.
 */
function pushInvoicesToAirtable() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('Invoices');
  if (!sheet) { Logger.log('No Invoices sheet found.'); return; }

  const lastRow = sheet.getLastRow();
  if (lastRow < 2) return;

  const data = sheet.getRange(2, 1, lastRow - 1, 9).getValues();
  let pushed = 0;

  // Load configured base ID from Script Properties
  const baseId = PropertiesService.getScriptProperties().getProperty('AIRTABLE_BASE_ID') || '';
  if (!baseId) {
    SpreadsheetApp.getUi().alert('Set AIRTABLE_BASE_ID in Script Properties first.');
    return;
  }

  data.forEach(row => {
    const [, invoiceNum, vendor, amount, dueDate, , , status] = row;
    if (status !== 'done' || !invoiceNum) return;

    const resp = apiPost(`/airtable/bases/${baseId}/tables/Invoices/records`, {
      fields: {
        'Invoice Number': invoiceNum,
        'Vendor': vendor,
        'Amount': amount,
        'Due Date': dueDate,
        'Status': 'Pending Review',
        'Source': 'Apps Script',
      },
    });

    if (!resp.error) {
      pushed++;
    }
    Utilities.sleep(250);
  });

  logToSheet('pushInvoicesToAirtable', 'success', { pushed });
  toast(`✅ Pushed ${pushed} invoice(s) to Airtable`);
}

// ── Invoice summary report ────────────────────────────────────────────────────

/**
 * Generate an AI-written summary of all invoices in the sheet.
 * Writes the summary to a new "Invoice Summary" sheet.
 */
function generateInvoiceSummary() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('Invoices');
  if (!sheet) return;

  const lastRow = sheet.getLastRow();
  const data = sheet.getRange(2, 1, lastRow - 1, 5).getValues();

  // Build a text description of all invoices
  const invoiceList = data
    .filter(r => r[1]) // has invoice number
    .map(r => `Invoice ${r[1]} from ${r[2]} for ${r[3]} due ${r[4]}`)
    .join('\n');

  if (!invoiceList) {
    SpreadsheetApp.getUi().alert('No processed invoices to summarise.');
    return;
  }

  toast('Generating summary with Claude AI...');

  const resp = apiPost('/ai/summarize', {
    text: 'Invoice summary:\n' + invoiceList,
    max_words: 150,
  });

  const summary = resp.summary || 'Could not generate summary.';

  // Write to Summary sheet
  let summarySheet = ss.getSheetByName('Invoice Summary');
  if (!summarySheet) summarySheet = ss.insertSheet('Invoice Summary');
  summarySheet.clearContents();
  summarySheet.appendRow(['📊 Invoice Summary — Generated by AI']);
  summarySheet.appendRow([new Date().toLocaleString()]);
  summarySheet.appendRow(['']);
  summarySheet.appendRow([summary]);
  summarySheet.getRange(1, 1).setFontWeight('bold').setFontSize(14);

  ss.setActiveSheet(summarySheet);
  toast('✅ Invoice summary generated');
  logToSheet('generateInvoiceSummary', 'success', { invoices: data.length });
}
