/**
 * WorkflowAutomation.gs — Core workflow integration with the FastAPI backend.
 *
 * Install triggers:
 *   Run `installTriggers()` once from the Apps Script editor to register
 *   all time-based and sheet-based triggers automatically.
 *
 * Menu:
 *   The custom menu is added via onOpen(). Reload the sheet to see it.
 */

// ── Menu ──────────────────────────────────────────────────────────────────────

/**
 * Adds the "⚡ AI Workflows" menu to Google Sheets.
 * Runs automatically when the spreadsheet is opened.
 */
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('⚡ AI Workflows')
    .addItem('🤖 Classify selected rows', 'classifySelectedRows')
    .addItem('📄 Summarise selected cell', 'summariseSelectedCell')
    .addSeparator()
    .addItem('📧 Process inbox emails', 'processInboxEmails')
    .addItem('📅 Sync calendar events', 'syncCalendarEvents')
    .addSeparator()
    .addItem('✨ AI-fill sheet with data', 'showAiFillDialog')
    .addItem('🔄 Trigger workflow via API', 'showTriggerWorkflowDialog')
    .addSeparator()
    .addItem('💚 Check API health', 'checkApiHealth')
    .addItem('📋 View execution logs', 'viewExecutionLogs')
    .addToUi();
}

// ── Health Check ──────────────────────────────────────────────────────────────

function checkApiHealth() {
  const health = apiGet('/health');
  if (health.error) {
    SpreadsheetApp.getUi().alert('❌ API Unreachable', health.message || 'Cannot connect to the API.', SpreadsheetApp.getUi().ButtonSet.OK);
    return;
  }

  const integrations = health.integrations || {};
  const lines = Object.entries(integrations).map(([name, info]) => {
    const icon = info.enabled ? '✅' : '○';
    return `${icon} ${name}: ${info.status}`;
  });

  SpreadsheetApp.getUi().alert(
    '💚 API Health — ' + (health.status || 'unknown'),
    `Version: ${health.version || '?'}\nEnv: ${health.environment || '?'}\n\nIntegrations:\n${lines.join('\n')}`,
    SpreadsheetApp.getUi().ButtonSet.OK
  );
}

// ── Workflow Trigger ──────────────────────────────────────────────────────────

function showTriggerWorkflowDialog() {
  const ui = SpreadsheetApp.getUi();
  const workflowsResp = apiGet('/workflows', { limit: 20 });

  if (workflowsResp.error || !workflowsResp.data) {
    ui.alert('❌ Could not load workflows. Make sure the API is running.');
    return;
  }

  if (workflowsResp.data.length === 0) {
    ui.alert('No workflows found. Create one via the API first.');
    return;
  }

  // Build a list of workflow names for the user to pick
  const names = workflowsResp.data.map((w, i) => `${i + 1}. [${w.status}] ${w.name}`).join('\n');
  const response = ui.prompt(
    '🔄 Trigger Workflow',
    `Enter the number of the workflow to execute:\n\n${names}`,
    ui.ButtonSet.OK_CANCEL
  );

  if (response.getSelectedButton() !== ui.Button.OK) return;

  const idx = parseInt(response.getResponseText().trim(), 10) - 1;
  if (isNaN(idx) || idx < 0 || idx >= workflowsResp.data.length) {
    ui.alert('Invalid selection.');
    return;
  }

  const wf = workflowsResp.data[idx];
  toast(`Triggering: ${wf.name}...`);

  const result = apiPost(`/workflows/${wf.id}/execute`, {
    source: 'apps_script',
    spreadsheet_id: SpreadsheetApp.getActiveSpreadsheet().getId(),
  });

  if (result.error) {
    ui.alert('❌ Execution failed: ' + result.message);
  } else {
    ui.alert(
      '✅ Workflow Executed',
      `Workflow: ${wf.name}\nStatus: ${result.status}\nExecution ID: ${result.execution_id}`,
      ui.ButtonSet.OK
    );
    logToSheet('trigger_workflow', result.status, { workflow: wf.name, id: result.execution_id });
  }
}

// ── Execution Logs ────────────────────────────────────────────────────────────

function viewExecutionLogs() {
  const resp = apiGet('/executions', { limit: 20 });
  if (resp.error || !resp.data) {
    SpreadsheetApp.getUi().alert('❌ Could not load executions.');
    return;
  }

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName('Execution Logs');
  if (!sheet) {
    sheet = ss.insertSheet('Execution Logs');
  } else {
    sheet.clearContents();
  }

  const headers = ['Execution ID', 'Workflow ID', 'Status', 'Triggered By', 'Duration (s)', 'Created At'];
  sheet.appendRow(headers);
  sheet.getRange(1, 1, 1, headers.length).setFontWeight('bold').setBackground('#1a56db').setFontColor('#ffffff');
  sheet.setFrozenRows(1);

  resp.data.forEach(ex => {
    sheet.appendRow([
      ex.id,
      ex.workflow_id,
      ex.status,
      ex.triggered_by || '',
      ex.duration_seconds || '',
      ex.created_at || '',
    ]);
  });

  // Colour-code status column
  const dataRange = sheet.getRange(2, 3, resp.data.length, 1);
  resp.data.forEach((ex, i) => {
    const cell = sheet.getRange(i + 2, 3);
    if (ex.status === 'success') cell.setBackground('#d1fae5');
    else if (ex.status === 'failed') cell.setBackground('#fee2e2');
    else cell.setBackground('#fef3c7');
  });

  sheet.autoResizeColumns(1, headers.length);
  ss.setActiveSheet(sheet);
  toast(`Loaded ${resp.data.length} executions into "Execution Logs" sheet`);
}

// ── Triggers Installation ─────────────────────────────────────────────────────

/**
 * Install all triggers. Run this ONCE from the Apps Script editor.
 */
function installTriggers() {
  // Remove existing triggers to avoid duplicates
  ScriptApp.getProjectTriggers().forEach(t => ScriptApp.deleteTrigger(t));

  // onOpen trigger (add menu)
  ScriptApp.newTrigger('onOpen')
    .forSpreadsheet(SpreadsheetApp.getActiveSpreadsheet())
    .onOpen()
    .create();

  // Time-based: process emails every hour
  ScriptApp.newTrigger('processInboxEmails')
    .timeBased()
    .everyHours(1)
    .create();

  // Time-based: sync calendar events daily at 8am
  ScriptApp.newTrigger('syncCalendarEvents')
    .timeBased()
    .atHour(8)
    .everyDays(1)
    .create();

  Logger.log('✅ All triggers installed');
  SpreadsheetApp.getUi().alert('✅ Triggers installed successfully!');
}
