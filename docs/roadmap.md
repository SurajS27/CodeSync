# CodeSync Project Roadmap

This roadmap outlines the plan for the next milestones leading up to the production-ready v1.0.0 release.

---

```
  v0.8: Submission Detection
            │
            ▼
  v0.9: Automatic Sync
            │
            ▼
  v1.0: Production Release
```

---

## Milestone v0.8: Submission Detection Engine

- **Goal**: Intercept user submissions on LeetCode and detect "Accepted" status transitions.
- **Deliverables**:
  - Content script injection monitoring LeetCode page AJAX queries or DOM network requests.
  - Listener checking submission button click events and loading panels.
  - Submission status DOM parser extracting result tags (e.g. "Accepted", "Wrong Answer").
  - Code editor parser extracting the user's submitted source code from the LeetCode monaco/code-area components.
- **Dependencies**: LeetCode Detection Engine (v0.7.0).
- **Success Criteria**:
  - Submitting code on LeetCode triggers the extension's submission checker.
  - If the submission results in "Accepted", the extension extracts the code and problem difficulty.
  - Incorrect submissions (e.g. "Time Limit Exceeded", "Wrong Answer") are ignored.

---

## Milestone v0.9: Automatic Sync Workflow

- **Goal**: Orchestrate end-to-end background synchronization without requiring manual copy-pasting or popup triggers.
- **Deliverables**:
  - Chrome Extension background queue worker to retry failed synchronizations.
  - API sync integration linking the Extension background worker to `POST /sync/leetcode`.
  - Notification toasts inside LeetCode pages showing sync progress (e.g. "Syncing to GitHub...", "Sync Completed!").
- **Dependencies**: Submission Detection Engine (v0.8.0), LeetCode Sync Foundation (v0.5.0).
- **Success Criteria**:
  - Clicking "Submit" and getting "Accepted" on LeetCode automatically commits the code and README to the target repository in the background.
  - Visual notification alerts indicate successful commits or logs error alerts on failures.

---

## Milestone v1.0: Production Release

- **Goal**: Harden extension security, package assets, and publish to the Chrome Web Store.
- **Deliverables**:
  - Production Web Store packaging (minifying code, removing developer debug utilities, setting `DEV_MODE = false`).
  - Production OAuth app setup with official redirects.
  - JWT token revocation management and database cleanup cron jobs.
  - Performance optimizations to reduce background worker memory footprint.
- **Dependencies**: v0.8.0, v0.9.0.
- **Success Criteria**:
  - The extension is published on the Chrome Web Store.
  - OAuth login redirect flow completes securely without manual copy-pasting.
  - Zero leakage of decrypted OAuth tokens at rest.
