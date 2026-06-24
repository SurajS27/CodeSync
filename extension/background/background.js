/**
 * CodeSync Background Service Worker
 * Serves as the extension's orchestrator and event listener foundation.
 */

chrome.runtime.onInstalled.addListener(() => {
  console.log("CodeSync Chrome Extension Foundation (v0.6.0) successfully installed.");
});

// Monitor storage updates to log session/settings lifecycle events
chrome.storage.onChanged.addListener((changes, namespace) => {
  if (namespace !== "local") return;

  if (changes.token) {
    const action = changes.token.newValue ? "saved" : "removed";
    console.log(`Authentication session token was ${action}.`);
  }

  if (changes.selectedRepositoryId) {
    console.log(`Active selected repository updated to: ${changes.selectedRepositoryId.newValue}`);
  }

  if (changes.apiBaseUrl) {
    console.log(`API Base URL setting updated to: ${changes.apiBaseUrl.newValue}`);
  }
});
