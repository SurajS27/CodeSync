# CodeSync Backend Service Architecture

This document covers the core architecture, layers, and service modules of the FastAPI backend application.

---

## Architecture Layers

```
  HTTP Client (Chrome Extension)
               │
               ▼
   [API Layer] Route Handlers (app/api/)
               │
               ▼
   [Service Layer] Business Logic (app/services/)
          ┌────┴────┐
          ▼         ▼
  [Data Models]   [External APIs]
  (app/models/)   (GitHub API)
```

1. **API Layer (`app/api/`)**: Manages routing, JSON serialization/deserialization, and validation. Implements route endpoints under `app/api/v1/`.
2. **Service Layer (`app/services/`)**: The core layer where business rules, algorithms, and logic flow are coordinated. Services are completely separated from HTTP routing concerns.
3. **Data Model Layer (`app/models/` & `app/database/`)**: Represents our PostgreSQL tables as SQLAlchemy models, managing transactions via async database sessions.
4. **Validation Schema Layer (`app/schemas/`)**: Pydantic validation structures mapping input payloads and formatting output JSON models.
5. **Core Config Layer (`app/core/`)**: Houses settings management (`config.py`), logging configurations (`logging.py`), and constants (`constants.py`).

---

## Core Services Reference

The service layer is composed of dedicated modules. Below is a detailed spec of every major backend service:

### 1. `GitHubOAuthService`
- **Purpose**: Manages communication with GitHub's OAuth server to authenticate users.
- **Responsibilities**:
  - Generates the secure target URL for GitHub OAuth redirects.
  - Exchanges authorization codes for user access tokens.
  - Fetches the user profile (id, login, avatar, email) from GitHub API.
- **Dependencies**: `httpx.AsyncClient` (network connection).
- **Control Flow**:
  1. Frontend asks for login target -> `get_authorization_url` returns GitHub redirect URL.
  2. GitHub callback redirects -> `exchange_code_for_token` exchanges code -> returns Access Token.
  3. Service calls `fetch_github_profile` to register user info.

### 2. `RepositoryService`
- **Purpose**: Performs local database CRUD operations for repositories.
- **Responsibilities**:
  - Creates, reads, updates, and deletes `Repository` database records.
  - Fetches repository status and commits audit history metadata.
- **Dependencies**: `AsyncSession` (database transactions).

### 3. `RepositoryBootstrapService`
- **Purpose**: Automatically bootstraps newly provisioned repository layouts.
- **Responsibilities**:
  - Writes standard baseline directories and configuration files on GitHub.
  - Commits `.gitignore` files, README files, and metadata configuration files (`metadata/config.json`).
  - Manages bootstrap execution states (`PENDING` -> `RUNNING` -> `COMPLETED`/`FAILED`).
- **Dependencies**: `GitHubRepositoryService`, `GitHubContentService`, `AsyncSession`.
- **Control Flow**:
  1. Receives repository ID and active user session.
  2. Sets `bootstrap_status` to `RUNNING` in the database.
  3. Commits `.gitignore`, `README.md`, and `metadata/config.json` via `GitHubContentService`.
  4. On success: Updates state to `COMPLETED` and saves timestamp. On fail: records error text and sets to `FAILED`.

### 4. `RepositoryAccessService`
- **Purpose**: Validates access control and repository ownership limits.
- **Responsibilities**:
  - Checks if a repository belongs to a specific user.
  - Raises `HTTPException(403)` or `HTTPException(404)` directly to safeguard data boundaries.
- **Dependencies**: `RepositoryService`.

### 5. `LeetCodeSyncService`
- **Purpose**: Orchestrates synchronization pipelines for coding solutions.
- **Responsibilities**:
  - Manages sync states (`PENDING` -> `RUNNING` -> `COMPLETED`/`FAILED`).
  - Coordinates path creators and checks file existence.
  - Commits solution codes and generated README files.
- **Dependencies**: `RepositoryAccessService`, `SyncHistoryService`, `PathGenerationService`, `GitHubContentService`, `AsyncSession`.
- **Control Flow**:
  1. Verifies user ownership on repository.
  2. Creates a `SyncHistory` log with status `PENDING`.
  3. Transitions status to `RUNNING`.
  4. Generates directories and files via `PathGenerationService`.
  5. Inspects repository on GitHub to see if target files exist (fetching SHAs if present to perform updates).
  6. Commits README description and solution file.
  7. Updates `SyncHistory` to `COMPLETED` with the commit SHA and URL details.

### 6. `SyncHistoryService`
- **Purpose**: Manages database CRUD operations for sync logs.
- **Responsibilities**:
  - Creates initial logs with `PENDING` states.
  - Updates commit URLs, SHAs, repository paths, and status fields.
  - Fetches audit trail logs for users.
- **Dependencies**: `AsyncSession`.

### 7. `PathGenerationService`
- **Purpose**: Determines repository path layouts and maps programming languages to file extensions.
- **Responsibilities**:
  - Formulates paths as `leetcode/{difficulty}/{problem_slug}/`.
  - Maps language strings to extensions (e.g. `python` -> `solution.py`, `javascript` -> `solution.js`).
  - Raises validation errors for unsupported languages.
- **Dependencies**: None (pure helper utility).
