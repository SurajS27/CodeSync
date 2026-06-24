# CodeSync Architectural Decisions (ADRs)

This document records the architectural decisions, contexts, alternatives considered, and consequences for key system designs.

---

## ADR 1: Why FastAPI?
- **Context**: CodeSync needs a fast, asynchronous backend web framework to handle I/O-bound integrations (network calls to GitHub and database queries to Neon).
- **Decision**: Select **FastAPI**.
- **Alternatives Considered**: Flask (synchronous, requires threading for async APIs), Django (bloated, complex async setup for microservices).
- **Consequences**:
  - Out-of-the-box integration with Pydantic for validation.
  - Native support for async/await async handlers.
  - Automatically generates interactive OpenAPI documentation (Swagger UI).

---

## ADR 2: Why SQLAlchemy & Alembic?
- **Context**: CodeSync needs a robust Object Relational Mapper (ORM) to model user details, repositories, and synchronizations. It also needs schema migration controls to update tables without data loss.
- **Decision**: Select **SQLAlchemy 2.x** and **Alembic**.
- **Alternatives Considered**: Tortoise ORM (lacks mature documentation), raw SQL queries via asyncpg (difficult to maintain and scale).
- **Consequences**:
  - Standardized ORM syntax with clean mappings.
  - Alembic auto-generates schema change scripts based on changes in class definitions.

---

## ADR 3: Why Neon Serverless PostgreSQL?
- **Context**: CodeSync needs an scalable, serverless relational database to store user metadata.
- **Decision**: Select **Neon PostgreSQL**.
- **Alternatives Considered**: SQLite (unsuitable for concurrent multi-user web hosts), AWS RDS (expensive for development).
- **Consequences**:
  - Serverless architecture scales down to zero when idle, saving costs.
  - Provides native PostgreSQL features like native JSON queries and SSL connection requirements.

---

## ADR 4: Why Manifest V3 & Vanilla JavaScript?
- **Context**: CodeSync needs a browser extension. It must meet browser extension store guidelines while staying fast.
- **Decision**: Select **Manifest V3** and **Vanilla JavaScript** (no frameworks).
- **Alternatives Considered**: React/Vue-based setup (requires bundling tools like Webpack, increases extension package size, harder to review).
- **Consequences**:
  - Avoids build pipeline overhead (we can load raw source directories directly as unpacked extensions).
  - Clean compliance with Manifest V3 service worker parameters.
  - Minimal memory footprint and startup latency.

---

## ADR 5: Why GitHub OAuth for Authentication?
- **Context**: The app must write files directly to users' GitHub repositories. We need access tokens without prompting users to paste raw Personal Access Tokens (PATs), which is insecure.
- **Decision**: Implement **GitHub OAuth**.
- **Alternatives Considered**: Personal Access Token (PAT) input fields (high friction, insecure if stored on client-side).
- **Consequences**:
  - High trust: users log in via GitHub's official consent page.
  - Scopes are explicitly limited to user repository access.

---

## ADR 6: Why SyncHistory exists?
- **Context**: Synchronization transactions can fail due to GitHub rate limits, internet drops, or repository renames. We need audits of every attempt.
- **Decision**: Create a dedicated **`sync_history`** audit table.
- **Alternatives Considered**: Stateless logging (difficult to track sync statistics or review past failures).
- **Consequences**:
  - Creates a reliable, auditable trail of sync states (`PENDING` -> `RUNNING` -> `COMPLETED`/`FAILED`).
  - Stores commit URLs, SHAs, and error logs for developer debugging.

---

## ADR 7: Why Repository Bootstrapping is Separate from Sync?
- **Context**: Each repository needs baseline config metadata (`metadata/config.json`, `.gitignore`) before syncs start. Doing this checks on every solution commit adds network latency.
- **Decision**: Implement a separate **Bootstrap Pipeline** triggered once during repository registration.
- **Alternatives Considered**: Bootstrapping on-demand during the first solution sync (makes the first sync request slow and adds complexity to the sync service).
- **Consequences**:
  - Speeds up the synchronization flow (saves 2-3 API round-trips).
  - Ensures clean repository layouts before solution uploads start.

---

## ADR 8: Why MutationObserver was chosen for LeetCode detection?
- **Context**: LeetCode uses client-side rendering (SPA). Page transitions do not trigger document reloads.
- **Decision**: Use a **`MutationObserver`** on `document.body` in the content script.
- **Alternatives Considered**: Periodic polling (`setInterval` every 2 seconds) (wastes CPU cycles and degrades browser performance).
- **Consequences**:
  - Listens to DOM changes in real-time.
  - Detects title and path changes immediately when a user clicks other challenges, updating extension states instantly.
