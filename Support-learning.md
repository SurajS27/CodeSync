# CodeSync Learning Support Reference

This document serves as an onboarding learning guide for developers transitioning to CodeSync. It compiles essential background materials, concepts, and technical links for the core technologies used in the project stack.

---

## Core Technologies & Reference Manuals

### 1. FastAPI
FastAPI is used to build our backend REST API. It utilizes Python type hints and Pydantic v2 to enforce request/response validations and automatically generate OpenAPI documents.
- **Key Concepts**: Dependency Injection (`Depends`), Pydantic validation models, ASGI lifespan context managers.
- **Recommended Reading**: [FastAPI Tutorial User Guide](https://fastapi.tiangolo.com/tutorial/)

### 2. Async SQLAlchemy 2.x & Psycopg v3
SQLAlchemy acts as our Object Relational Mapper (ORM). We use its async engine configurations combined with Psycopg v3 (via psycopg-binary) to perform non-blocking PostgreSQL database transactions.
- **Key Concepts**: `Mapped` and `mapped_column` type annotations, `select()` query statements, `AsyncSession` transactional workflows (`commit`, `rollback`, `refresh`).
- **Recommended Reading**: [SQLAlchemy 2.0 Unified Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/index.html)

### 3. Alembic
Alembic is our database migration tool. It auto-generates schema change files based on our database model classes.
- **Key Concepts**: Migration heads, upgrading (`upgrade()`), downgrading (`downgrade()`), custom enum handling (`checkfirst=True` checks).
- **Recommended Reading**: [Alembic Tutorial Documentation](https://alembic.sqlalchemy.org/en/latest/tutorial.html)

### 4. Chrome Extension Manifest V3
Manifest V3 is Chrome's modern platform for building browser extensions, designed for security, privacy, and performance.
- **Key Concepts**: Service Workers (Background scripts), Content Scripts (DOM extraction and listeners), Chrome Action Badges, Message Passing (`chrome.runtime.sendMessage`, `chrome.runtime.onMessage`), Local Storage (`chrome.storage.local`).
- **Recommended Reading**: [Chrome Extensions Developer Guide](https://developer.chrome.com/docs/extensions/mv3/getstarted/)

### 5. GitHub Integrations
- **GitHub OAuth API**: Securely exchanges authorization codes for user access tokens.
- **GitHub REST Contents API**: Manages files inside user repositories (creating, reading, and updating repository layout configurations).
- **Recommended Reading**: [GitHub REST API Documentation - Repositories Contents](https://docs.github.com/en/rest/repos/contents)

---

## Technical Onboarding Flow

To get familiar with CodeSync's implementation, we recommend reviewing our internal documents in order:

1. **[System Architecture](file:///d:/CodeSync/CodeSync/docs/architecture.md)**: Conceptualize the user flow, sequence interactions, and network request hops.
2. **[Database Schema Design](file:///d:/CodeSync/CodeSync/docs/database.md)**: Explore the table mappings and relationships.
3. **[API Specifications](file:///d:/CodeSync/CodeSync/docs/api-reference.md)**: Walk through endpoint parameters and formats.
4. **[Local Setup Tutorial](file:///d:/CodeSync/CodeSync/docs/local-development.md)**: Configure your workspace locally and verify your installation.
