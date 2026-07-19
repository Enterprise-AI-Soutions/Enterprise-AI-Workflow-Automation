/**
 * Config.gs — Shared configuration for all Apps Script files.
 *
 * HOW TO USE:
 * 1. In the Apps Script editor, go to Project Settings → Script Properties
 * 2. Add: API_BASE_URL = https://your-api-domain.com/api/v1
 *         (or http://localhost:8000/api/v1 for local dev with ngrok)
 */

// ── Configuration ─────────────────────────────────────────────────────────────

/**
 * Get the FastAPI base URL from Script Properties.
 * Falls back to localhost for development.
 */
function getApiBaseUrl() {
  const props = PropertiesService.getScriptProperties();
  return props.getProperty('API_BASE_URL') || 'http://localhost:8000/api/v1';
}

/**
 * Make an authenticated POST request to the FastAPI backend.
 * @param {string} endpoint - e.g. '/ai/classify'
 * @param {Object} payload - JSON body
 * @returns {Object} Parsed JSON response
 */
function apiPost(endpoint, payload) {
  const url = getApiBaseUrl() + endpoint;
  const options = {
    method: 'POST',
    contentType: 'application/json',
    payload: JSON.stringify(payload),
    muteHttpExceptions: true,
  };

  try {
    const response = UrlFetchApp.fetch(url, options);
    const code = response.getResponseCode();
    const text = response.getContentText();

    if (code >= 400) {
      Logger.log('API error %d at %s: %s', code, endpoint, text);
      return { error: true, status: code, message: text };
    }

    return JSON.parse(text);
  } catch (e) {
    Logger.log('Network error at %s: %s', endpoint, e.message);
    return { error: true, message: e.message };
  }
}

/**
 * Make an authenticated GET request to the FastAPI backend.
 * @param {string} endpoint - e.g. '/workflows'
 * @param {Object} [params] - Optional query params
 * @returns {Object} Parsed JSON response
 */
function apiGet(endpoint, params) {
  let url = getApiBaseUrl() + endpoint;
  if (params) {
    const qs = Object.entries(params)
      .map(([k, v]) => encodeURIComponent(k) + '=' + encodeURIComponent(v))
      .join('&');
    url += '?' + qs;
  }

  const options = { method: 'GET', muteHttpExceptions: true };

  try {
    const response = UrlFetchApp.fetch(url, options);
    const code = response.getResponseCode();
    if (code >= 400) {
      return { error: true, status: code };
    }
    return JSON.parse(response.getContentText());
  } catch (e) {
    return { error: true, message: e.message };
  }
}

/**
 * Show a toast notification in Google Sheets.
 * @param {string} message
 * @param {string} [title='Enterprise AI']
 */
function toast(message, title) {
  try {
    SpreadsheetApp.getActiveSpreadsheet().toast(message, title || 'Enterprise AI', 5);
  } catch (_) {
    Logger.log(message);
  }
}

/**
 * Log an entry to a "Logs" sheet in the active spreadsheet.
 * Creates the sheet if it doesn't exist.
 */
function logToSheet(action, status, detail) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let logSheet = ss.getSheetByName('_AI_Logs');
  if (!logSheet) {
    logSheet = ss.insertSheet('_AI_Logs');
    logSheet.appendRow(['Timestamp', 'Action', 'Status', 'Detail']);
    logSheet.getRange(1, 1, 1, 4).setFontWeight('bold').setBackground('#1a56db').setFontColor('#ffffff');
    logSheet.setFrozenRows(1);
  }
  logSheet.appendRow([new Date().toISOString(), action, status, JSON.stringify(detail)]);
}
