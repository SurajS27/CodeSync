# Chrome Extension Guide (v0.7.0)

This guide documents the architecture, script communication flows, data models, and LeetCode page detection mechanics of the CodeSync Chrome Extension.

---

## 1. Extension Directory Map

The extension is structured using standard vanilla components to preserve performance:

```
extension/
├── manifest.json       # Manifest V3 Configuration
├── background/
│   └── background.js   # Background service worker (monitors tab activations)
├── content/
│   └── content_detect.js # Content script parsing LeetCode pages
├── scripts/
│   ├── storage.js      # chrome.storage.local helper wrapper
│   ├── state.js        # State manager abstraction
│   └── api.js          # Shared API client
├── popup/
│   ├── popup.html      # Glassmorphic Dark UI layout
│   ├── popup.css       # Layout styles & badges
│   └── popup.js        # Auth state loader & repo selector
└── options/
    ├── options.html    # Connection setting view
    ├── options.css     # Settings page styles
    └── options.js      # Endpoint updates & repository choices handler
```

---

## 2. Scripts & Module Responsibilities

### Background Service Worker (`background.js`)
- Runs in the background of the browser lifecycle.
- Monitors browser tab events (`chrome.tabs.onActivated` and `chrome.tabs.onUpdated`).
- Intercepts messages dispatched by content scripts and modifies the extension action toolbar badge (`E`, `M`, or `H`) and badge background color dynamically.

### Content Script (`content_detect.js`)
- Runs in the isolated context of matching LeetCode tabs (`leetcode.com/problems/*`).
- Parses DOM metadata, handles single-page app (SPA) path changes, and dispatches data to the background.

### Popup Script (`popup.js`)
- Runs when the popup card is active. Handles profile validations, populates target repo inputs, and updates layouts in real-time.

### Shared Utility Clients (`api.js`, `storage.js`, `state.js`)
- Designed as ES modules to prevent code duplication:
  - **`storage.js`**: Provides Promise-wrapped local storage calls.
  - **`state.js`**: Abstracted queries for auth statuses.
  - **`api.js`**: Performs HTTP fetches, injects headers, and clears state on `401 Unauthorized` sessions.

---

## 3. Communication Flow

```
+--------------------------+
|  leetcode.com/problems/  |
|      (Active Page)       |
+------------+-------------+
             |
             | [DOM Parsing]
             v
+--------------------------+
|      Content Script      |
|    (content_detect.js)   |
+------------+-------------+
             |
             | [chrome.runtime.sendMessage]
             | Payload: PROBLEM_DETECTED
             v
+--------------------------+
| Background Worker        |
|    (background.js)       |
+------------+-------------+
             |
             | [chrome.storage.local.set]
             | Key: current_problem
             v
+--------------------------+         +--------------------------+
|   chrome.storage.local   | <-----> |     Popup Controller     |
|         (Storage)        |         |        (popup.js)        |
+--------------------------+         +--------------------------+
                                         (onChanged event fires)
```

---

## 4. Detection Engine Mechanics

### URL Route Validation
The content script ignores overall list pages, solutions tabs, and contest paths:
- Matching paths: `/problems/*`
- Ignores: `/problemset/`, `/submissions/`, `/solutions/`, `/contest/`.

### Metadata Extraction
- **Slug**: Parsed from `window.location.pathname` (e.g. `/problems/two-sum/` -> `two-sum`).
- **Title**: Scans `div.text-title-large` or `div[data-cy="question-title"]`. Falls back to parsing `document.title` and strips leading numerals (e.g., "105. Construct Tree" -> "Construct Tree").
- **Difficulty**: Checks exact text equivalence of elements (`text === "easy" || text === "medium" || text === "hard"`) targeting class selectors (`.text-difficulty-easy`, `.text-brand-orange`, etc.) to prevent false substring matches.

### SPA Navigation
LeetCode is a Single Page Application (SPA) where pages load without full document reloads. To capture these transitions:
1. **MutationObserver**: Content script instantiates a `MutationObserver` watching `document.body` for subtree insertions and child nodes mutations.
2. **Debounce / Change Check**: The content script verifies if the slug or title has modified before sending message payloads, preventing background messaging spam.
3. **Backup Poll**: Runs a backup interval poll every 8 seconds.

---

## 5. Toolbar Badge States

The background service worker updates color-coded badges to indicate difficulty:
- **Easy**: Letter: `E`, Color: Green (`#10b981`)
- **Medium**: Letter: `M`, Color: Orange (`#f59e0b`)
- **Hard**: Letter: `H`, Color: Red (`#ef4444`)

When the user switches tabs, the background service worker evaluates the active URL. If it represents a non-LeetCode page, the badge is hidden. The stored `current_problem` is preserved so users can still view it in the popup.
