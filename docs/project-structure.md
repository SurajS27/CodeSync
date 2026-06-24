# CodeSync Directory Structure

This document provides a directory map of the CodeSync project, detailing folder hierarchies, module responsibilities, and key files.

---

## High-Level Folder Layout

```
CodeSync/
├── backend/            # FastAPI REST API Backend
├── extension/          # Manifest V3 Chrome Extension
└── docs/               # System Documentation & ADRs
```

---

## 1. Backend Service (`backend/`)

The backend is built as a modular FastAPI python application:

```
backend/
├── alembic/            # Database schema migration revision scripts
│   └── versions/       # Python scripts tracking table modifications
├── app/                # Main application core
│   ├── api/            # Route handlers & endpoints
│   │   ├── deps/       # Dependency injection helpers (JWT verification, DB sessions)
│   │   └── v1/         # Version 1 API endpoint routers
│   ├── core/           # Configuration, logging utilities, and global constants
│   ├── database/       # DB session creators and Declarative Base class
│   ├── models/         # SQLAlchemy database models
│   ├── schemas/        # Pydantic schema validation models
│   ├── services/       # Core business logic and database CRUD helpers
│   └── utils/          # Token encryption & cryptographic helpers
├── alembic.ini         # Alembic database migration config file
├── requirements.txt    # Python package dependencies manifest
└── .env.example        # Environment variable template
```

### Folder Responsibilities:
- **`app/api/v1/`**: Receives incoming HTTP requests, maps queries, validates input parameters, calls appropriate service layers, and returns JSON payloads.
  - *Example*: `api/v1/sync.py` implements the `/sync/leetcode` POST endpoint.
- **`app/models/`**: Declares database entities mapped to SQLAlchemy classes.
  - *Example*: `models/sync_history.py` represents the sync log audit table.
- **`app/schemas/`**: Declares request and response body data validations via Pydantic.
  - *Example*: `schemas/sync.py` validates fields in `LeetCodeSyncRequest`.
- **`app/services/`**: Orchestrates operations, connects API endpoints to database transactions, and manages communications with external GitHub endpoints.
  - *Example*: `services/leetcode_sync_service.py` executes file checks and commits solutions.
- **`app/utils/`**: Implements cryptographic utilities for data safety.
  - *Example*: `utils/encryption.py` encrypts and decrypts user OAuth access tokens.

---

## 2. Chrome Extension (`extension/`)

The extension is implemented using Vanilla JavaScript and Manifest V3 specifications:

```
extension/
├── background/         # Background scripts
│   └── background.js   # Extension service worker (badge manager, tab states)
├── content/            # Content scripts
│   └── content_detect.js # DOM parsing and LeetCode problem page detection
├── options/            # Options configuration page
│   ├── options.html    # Configuration view layout
│   ├── options.css     # Settings page styles
│   └── options.js      # Endpoint updates & repository choices handler
├── popup/              # Action popup UI
│   ├── popup.html      # Main popup interface
│   ├── popup.css       # Sleek dark styles
│   └── popup.js        # Auth validations, profile display, repo selection
└── scripts/            # Shared clients modules
    ├── api.js          # HTTP requests and backend endpoints connector
    ├── storage.js      # chrome.storage.local helper wrapper
    └── state.js        # Session state manager abstraction
```

### Folder Responsibilities:
- **`background/`**: Runs in the background as a service worker to coordinate tab switches and manage action badges.
- **`content/`**: Runs in the context of the user's browser pages to detect active problems and read DOM elements.
- **`popup/`**: Renders the interface when clicking the extension icon.
- **`options/`**: Renders settings page when clicking settings or opening extension options.
- **`scripts/`**: Houses utility classes (API, Storage, State) loaded as ES modules to prevent duplication across popup and options controllers.
