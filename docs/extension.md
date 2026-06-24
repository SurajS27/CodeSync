# Chrome Extension Guide (v0.8.0)

This guide documents the architecture, script communication flows, data models, LeetCode page detection, and submission capture mechanics of the CodeSync Chrome Extension.

---

## 1. Extension Directory Map

The extension is structured using standard vanilla components to preserve performance:

```
extension/
├── manifest.json       # Manifest V3 Configuration
├── background/
│   └── background.js   # Background service worker (monitors tab activations, stores submissions)
├── content/
│   ├── content_detect.js     # Content script parsing LeetCode active problems
│   └── submission_detector.js # Content script detecting and parsing accepted submissions
├── scripts/
│   ├── storage.js      # chrome.storage.local helper wrapper
│   ├── state.js        # State manager abstraction
│   └── api.js          # Shared API client
├── popup/
│   ├── popup.html      # Glassmorphic Dark UI layout
│   ├── popup.css       # Layout styles & badges
│   └── popup.js        # Auth state loader & repo/submission renderer
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
- Receives validated `SUBMISSION_DETECTED` events, filters out redundant updates, manages the latest submission state in local storage, and maintains a rolling **20-entry history stack** (`submission_history`).

### Problem Detection Script (`content_detect.js`)
- Runs in the isolated context of matching LeetCode tabs (`leetcode.com/problems/*`).
- Parses DOM metadata, handles single-page app (SPA) path changes, and dispatches problem metadata to the background.

### Submission Detection Script (`submission_detector.js`)
- Injected on LeetCode problem paths.
- Monitors the page using a `MutationObserver` to watch for successful "Accepted" submission tags.
- Extracts unique submission IDs, normalizes programming languages, scrapes editor content from Monaco lines, and extracts runtime/memory metrics.

### Popup Script (`popup.js`)
- Runs when the popup card is active. Handles profile validations, populates target repo inputs, and updates active problem and latest submission cards in real-time.

### Shared Utility Clients (`api.js`, `storage.js`, `state.js`)
- Designed as ES modules to prevent code duplication:
  - **`storage.js`**: Provides Promise-wrapped local storage calls.
  - **`state.js`**: Abstracted queries for auth statuses.
  - **`api.js`**: Performs HTTP fetches, injects headers, and clears state on `401 Unauthorized` sessions.

---

## 3. Communication Flow

```
+------------------------------------+
|       leetcode.com/problems/       |
|            (Active Page)           |
+-----------------+------------------+
                  |
        +---------+---------+
        |                   | [DOM Parsing]
        v                   v
+------------------+ +----------------------+
|  Content Script  | |    Content Script    |
| (content_detect) | | (submission_detector)|
+--------+---------+ +----------+-----------+
         |                      |
         | [PROBLEM_DETECTED]   | [SUBMISSION_DETECTED]
         +----------+-----------+
                    | (chrome.runtime.sendMessage)
                    v
         +----------------------+
         |  Background Worker   |
         |    (background.js)   |
         +----------+-----------+
                    | (chrome.storage.local.set)
                    +--------------------+
                    |                    |
                    v                    v
         +--------------------+ +--------------------+
         |  current_problem   | | latest_submission  |
         +---------+----------+ +---------+----------+
                   |                      |
                   +----------+-----------+
                              | (onChanged event)
                              v
         +-------------------------------------------+
         |          Popup UI (popup.js)              |
         +-------------------------------------------+
```

---

## 4. Detection Engine Mechanics

### URL Route Validation
The problem content script ignores overall list pages, solutions tabs, and contest paths:
- Matching paths: `/problems/*`
- Ignores: `/problemset/`, `/submissions/`, `/solutions/`, `/contest/`.

### Metadata Extraction
- **Slug**: Parsed from `window.location.pathname` (e.g. `/problems/two-sum/` -> `two-sum`).
- **Title**: Scans `div.text-title-large` or `div[data-cy="question-title"]`. Falls back to parsing `document.title` and strips leading numerals (e.g., "105. Construct Tree" -> "Construct Tree").
- **Difficulty**: Checks exact text equivalence of elements (`text === "easy" || text === "medium" || text === "hard"`) targeting class selectors (`.text-difficulty-easy`, `.text-brand-orange`, etc.) to prevent false substring matches.

---

## 5. Submission Detection Engine Mechanics

### Accepted Submission Status
- Scans container labels for text matching or starting with `"accepted"` (case-insensitive) to handle strings containing testcase progress (e.g., `"Accepted 11511 / 11511 testcases passed"`).

### Code Scraper Hierarchy
Uses a descending order of fallbacks:
1. Monaco Editor Line text content scraper (joins `.view-line` texts with `\n` to preserve indents and spaces).
2. Monaco Editor Line innerText scraper.
3. Fallback code block selectors (`pre`, `code`, `textarea.inputarea`).
4. Rejects any code content with length `<= 5` characters.

### Language Normalization
Extracts from code selector dropdowns, headers (e.g., matching the `"Code | <Lang>"` label pattern), or elements with text matching known languages. Normalizes variables to: `python`, `javascript`, `typescript`, `java`, `cpp`, `c`, `go`, `rust`, `csharp`.

### Metrics & Async State Checks
Because runtime and memory parameters are fetched and rendered asynchronously after the submission ID is updated:
1. **Container Scans**: Matches parents of elements containing `"Runtime"` and `"Memory"` to extract the metric values (e.g. `3 ms`, `19.15 MB`).
2. **Updates Permitted**: Duplicate checking matches **both** the submission ID and the metric parameters. If metrics load after the initial extraction passes, the system updates the stored log rather than ignoring the event as a duplicate.

---

## 6. Toolbar Badge States

The background service worker updates color-coded badges to indicate difficulty:
- **Easy**: Letter: `E`, Color: Green (`#10b981`)
- **Medium**: Letter: `M`, Color: Orange (`#f59e0b`)
- **Hard**: Letter: `H`, Color: Red (`#ef4444`)

When the user switches tabs, the background service worker evaluates the active URL. If it represents a non-LeetCode page, the badge is hidden. The stored `current_problem` is preserved so users can still view it in the popup.
