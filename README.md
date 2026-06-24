# CodeSync

CodeSync is a developer productivity tool that automatically synchronizes solved coding challenges (e.g., from LeetCode) directly to a provisioned, structured GitHub repository. It ensures developers can maintain an automated, centralized, and clean portfolio of their problem-solving achievements.

---

## The Problem Solved

Software developers solve hundreds of algorithm challenges on platforms like LeetCode to improve their skills and prepare for technical interviews. However:
1. **Manual Effort**: Copy-pasting code, creating structured directories, and writing README problem descriptions in a GitHub repository is tedious and rarely kept up-to-date.
2. **Scatter**: Solved submissions remain locked inside the coding platform, inaccessible as a structured portfolio for recruiters.
3. **Friction**: Existing browser extensions are often unmaintained, require manual file uploads, or store tokens insecurely in plaintext.

**CodeSync** automates this by detecting solved problems, structuring folders on GitHub automatically, creating description files, committing solution codes, and keeping a secure, auditable history of synchronizations.

---

## Core Features

- **GitHub OAuth Login**: Simple, secure authentication yielding a stateless backend JWT.
- **Repository Provisioning & Auto-Bootstrapping**: Automatically creates a GitHub repository and bootstraps it with a structured layout, `.gitignore`, and configuration metadata.
- **LeetCode Detection Engine**: Content script detects visited challenge pages, extracts details (Title, Slug, Difficulty, URL), and updates extension status badges (`E`/`M`/`H`) in real-time.
- **Idempotent Sync Pipeline**: Commits solutions and problem READMEs to structured folders (e.g. `leetcode/easy/two-sum/`). Updates existing files without duplicate commits.
- **Auditable Sync History**: Keeps local database records of every sync event (`PENDING` -> `RUNNING` -> `COMPLETED`/`FAILED`) with commit URLs and SHAs.

---

## Technology Stack

- **Backend**: FastAPI, Async SQLAlchemy 2.x, Alembic, PostgreSQL (via Neon Serverless), Psycopg v3.
- **Chrome Extension**: Manifest V3, Vanilla JavaScript, Chrome Storage API, Content Scripts, Service Worker.
- **Integrations**: GitHub OAuth API, GitHub REST Contents API.

---

## System Architecture

```
+-------------------------------------------------------------+
|                     Chrome Extension                        |
|  [Popup UI] <---> [Storage Client] <---> [Content Script]   |
+------------------------------+------------------------------+
                               | (JWT Auth / REST API)
                               v
+-------------------------------------------------------------+
|                     FastAPI Backend                         |
|   [Routers] <---> [Services] <---> [SQLAlchemy ORM]         |
+-------------------+----------------------+------------------+
                    |                      |
                    v                      v
        +-----------------------+  +-----------------------+
        |  PostgreSQL Database  |  |      GitHub API       |
        |   (Neon Serverless)   |  |   (REST v3 Client)    |
        +-----------------------+  +-----------------------+
```

---

## Screenshots Placeholders

### 1. GitHub OAuth Authorization
*Redirects user securely to GitHub for application authorization, yielding a custom API JWT.*

### 2. Repository Provisioning
*Provisions a new repository or links an existing one, triggering the layout bootstrapping.*

### 3. Extension Popup UI
*A sleek dark-mode glassmorphic popup containing user profiles, target repository select inputs, active challenge metadata, and sync statuses.*

### 4. LeetCode Active Page Detection
*Content scripts parse problem pages, updating the toolbar extension action badge with color-coded difficulty levels (Green E, Orange M, Red H).*

---

## Quick Start

### 1. Spin up the Backend API
1. Navigate to the backend folder and activate your virtual environment:
   ```bash
   cd backend
   .venv\Scripts\activate
   ```
2. Set up your `.env` configuration file containing Neon database connection strings and GitHub OAuth Client credentials.
3. Start the server using Uvicorn:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

### 2. Install the Chrome Extension
1. Open Google Chrome and go to `chrome://extensions/`.
2. Enable **Developer mode** in the top-right corner.
3. Click **Load unpacked** and select the `extension/` directory.
4. Pin **CodeSync** to your browser toolbar.

---

## Documentation Index

Comprehensive guides for developers are available in the [docs/](file:///d:/CodeSync/CodeSync/docs/) directory:

- **[System Architecture](file:///d:/CodeSync/CodeSync/docs/architecture.md)**: Deep dive with sequence diagrams.
- **[Project Directory Map](file:///d:/CodeSync/CodeSync/docs/project-structure.md)**: Project layout explanation.
- **[Backend Service Guide](file:///d:/CodeSync/CodeSync/docs/backend.md)**: FastAPI services, routers, and layers.
- **[Database Models & Schema](file:///d:/CodeSync/CodeSync/docs/database.md)**: Table definitions, constraints, and ERD.
- **[API Endpoint Specifications](file:///d:/CodeSync/CodeSync/docs/api-reference.md)**: Payloads and request details.
- **[GitHub Integration Mechanics](file:///d:/CodeSync/CodeSync/docs/github-integration.md)**: OAuth flows and Contents API writes.
- **[Chrome Extension Guide](file:///d:/CodeSync/CodeSync/docs/extension.md)**: MV3 scripts, storage models, and message passing.
- **[Local Development Setup](file:///d:/CodeSync/CodeSync/docs/local-development.md)**: Step-by-step onboarding walkthrough.
- **[Testing Guidelines](file:///d:/CodeSync/CodeSync/docs/testing.md)**: Manual verification and automation tests.
- **[Milestones Archive](file:///d:/CodeSync/CodeSync/docs/milestones.md)**: Recap of milestones v0.1 through v0.8.
- **[Project Roadmap](file:///d:/CodeSync/CodeSync/docs/roadmap.md)**: Future milestones.
- **[Security Practices](file:///d:/CodeSync/CodeSync/docs/security.md)**: Tokens, encryption, and validations.
- **[Architectural Decisions (ADRs)](file:///d:/CodeSync/CodeSync/docs/decisions.md)**: Design rationales.

---

## Contributing

Please read [CONTRIBUTING.md](file:///d:/CodeSync/CodeSync/CONTRIBUTING.md) for details on our code style, branching strategies, and pull request review criteria.