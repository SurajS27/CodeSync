# CodeSync Project Milestones

This archive documents the historical progress, features, tests, and architectural evolutions of completed milestones (v0.1 to v0.7).

---

## Milestone v0.1: Backend Foundation
- **Goal**: Establish the core backend infrastructure and database connections.
- **Features**: FastAPI application setup, async logging middleware, health check endpoint, Neon serverless PostgreSQL integration using SQLAlchemy 2.x, and Alembic migrations framework setup.
- **Files Created**: `app/main.py`, `app/core/config.py`, `app/core/logging.py`, `app/database/session.py`, `app/api/v1/health.py`, `alembic.ini`.
- **Verification**: Verified health check route returned `200 OK` database status and logging middleware captured request paths.
- **Lessons Learned**: Neon database connection strings require async-compatible drivers (psycopg v3 via `postgresql+psycopg`) instead of classic sync psycopg2 drivers.

---

## Milestone v0.2: GitHub OAuth + JWT Auth
- **Goal**: Implement secure user authorization.
- **Features**: GitHub OAuth code exchange flow, AES encryption for storing user access tokens securely, database user registration, JWT generation, and endpoint protection dependencies.
- **Files Created**: `app/api/v1/auth.py`, `app/api/deps/auth.py`, `app/core/security.py`, `app/utils/encryption.py`, `app/models/user.py`.
- **Verification**: Tested login redirect generation, mock code callback flows, database registration, and token validation.
- **Lessons Learned**: Keeping tokens encrypted at rest via symmetric Fernet key cryptography ensures that database leaks do not compromise user GitHub accounts.

---

## Milestone v0.3: Repository Provisioning
- **Goal**: Provision developer target repositories on GitHub.
- **Features**: GitHub API integrations to create repositories, owner validation rules, and repo metadata logging.
- **Files Created**: `app/api/v1/repositories.py`, `app/services/github_repository_service.py`, `app/services/repository_service.py`, `app/models/repository.py`.
- **Verification**: Executed repository creation calls via Swagger UI and verified private repo generation on GitHub.
- **Lessons Learned**: Handled `422 Unprocessable Entity` gracefully when a repository already exists on GitHub by fetching its metadata instead of raising an error.

---

## Milestone v0.4: Workspace Bootstrapping
- **Goal**: Bootstrap workspace structures in provisioned repositories.
- **Features**: Committing `.gitignore`, `README.md`, and `metadata/config.json` baseline files, and tracking bootstrap state records.
- **Files Created**: `app/services/repository_bootstrap_service.py`, `app/services/github_content_service.py`.
- **Verification**: Inspected newly created repositories on GitHub to confirm files exist and contain appropriate titles and versions.
- **Lessons Learned**: Truncating exception strings stored in database logs (limit to 2000 chars) prevents oversized write failures on database crash reports.

---

## Milestone v0.5: LeetCode Sync Foundation
- **Goal**: Implement solution file commits and sync history tracking.
- **Features**: Created the `SyncHistory` database schema and enums, implemented path formatting rules (e.g. `leetcode/easy/two-sum/`), generated problem description READMEs, and committed solutions to GitHub.
- **Files Created**: `app/models/sync_history.py`, `app/models/enums.py`, `app/schemas/sync.py`, `app/services/path_generation_service.py`, `app/services/sync_history_service.py`, `app/services/leetcode_sync_service.py`.
- **Verification**: Tested pipeline execution using Swagger UI. Checked folder layouts and contents on GitHub, and verified sync logs database entries.
- **Lessons Learned**: Enforced idempotency check by querying file SHAs before committing, avoiding duplicate write conflicts from GitHub API.

---

## Milestone v0.6: Chrome Extension Foundation
- **Goal**: Build the Chrome Extension base layout and API integrations.
- **Features**: MV3 configurations, shared API/Storage modules, background scripts, popup layouts, settings options, and login authorization options.
- **Files Created**: `extension/manifest.json`, `extension/background/background.js`, `extension/scripts/storage.js`, `extension/scripts/api.js`, `extension/scripts/state.js`, `extension/popup/*`, `extension/options/*`.
- **Verification**: Loaded unpacked extension, tested connection settings updates, verified manual JWT token entry, and retrieved profiles.
- **Lessons Learned**: Modularizing client logic as ES modules (`api.js`, `storage.js`) prevents script duplication and keeps popup/options controllers clean.

---

## Milestone v0.7: LeetCode Detection Engine
- **Goal**: Enable challenge page parsing and action badge indicators.
- **Features**: Added content scripts matching LeetCode paths, implemented exact-match DOM parsers for slugs/titles/difficulties, handled SPA navigations using a `MutationObserver` on `document.body`, and updated toolbar badges dynamically.
- **Files Created**: `extension/content/content_detect.js`.
- **Verification**: Navigated through Easy/Medium/Hard problems on LeetCode. Checked badge updates (`E`/`M`/`H`), active problem popups rendering, and storage updates.
- **Lessons Learned**: Difficulty selectors must check for **exact string matching** rather than substring regex checks to prevent false positive matches on other elements (e.g., editorial tabs) sharing color classes.
