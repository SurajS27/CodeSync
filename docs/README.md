# CodeSync Developer Portal

Welcome to the CodeSync Developer Documentation. This directory contains detailed manuals, diagrams, and onboarding references to help you understand the codebase and begin contributing features immediately.

---

## Documentation Index

- **[System Architecture Guide](file:///d:/CodeSync/CodeSync/docs/architecture.md)**
  - Detailed system topology, Mermaid sequence diagrams for authentication, repository provisioning, repository layout bootstrapping, solution synchronization, and page detection flows.
- **[Project Directory Map](file:///d:/CodeSync/CodeSync/docs/project-structure.md)**
  - Codebase layout overview and file-level responsibilities.
- **[Backend Service Layers](file:///d:/CodeSync/CodeSync/docs/backend.md)**
  - REST API structure, SQLAlchemy async ORM layers, and service responsibilities.
- **[Database Models & Schemas](file:///d:/CodeSync/CodeSync/docs/database.md)**
  - Schema details (fields, enums, indexes, constraints) for `users`, `repositories`, and `sync_history`, including an ERD diagram.
- **[API Endpoint Reference](file:///d:/CodeSync/CodeSync/docs/api-reference.md)**
  - Fully documented endpoints for Auth, Repositories, and Sync actions. Includes payloads, parameters, responses, and error conditions.
- **[GitHub Integration Mechanics](file:///d:/CodeSync/CodeSync/docs/github-integration.md)**
  - Deep-dive into OAuth exchanges, repository creation, layout bootstrapping, and the REST Contents API for idempotent commits.
- **[Chrome Extension Architecture](file:///d:/CodeSync/CodeSync/docs/extension.md)**
  - Manifest V3 configuration, background service workers, content script selectors, local storage models, dynamic badges, and popup UI modules.
- **[Local Development Setup](file:///d:/CodeSync/CodeSync/docs/local-development.md)**
  - step-by-step onboarding guide, prerequisite setups, database migrations, and setting up the Chrome extension locally in developer mode.
- **[Testing & Verification Guide](file:///d:/CodeSync/CodeSync/docs/testing.md)**
  - Manual verification instructions, local checklists, and troubleshooting tips.
- **[Troubleshooting Guide](file:///d:/CodeSync/CodeSync/docs/troubleshooting.md)**
  - Resolving database connection errors, Pydantic settings bugs, badge loading failures, and migration conflicts.
- **[Milestones Archive](file:///d:/CodeSync/CodeSync/docs/milestones.md)**
  - Details on completed milestones (v0.1 to v0.7), including files created, testing done, and key learnings.
- **[Future Project Roadmap](file:///d:/CodeSync/CodeSync/docs/roadmap.md)**
  - Specifications for future milestones (v0.8 Submission Detection, v0.9 Auto-Sync, and v1.0 Production Release).
- **[Security Practices & Architecture](file:///d:/CodeSync/CodeSync/docs/security.md)**
  - Token encryption, JWT authentication mechanisms, access controls, and storage security models.
- **[Architectural Decisions (ADRs)](file:///d:/CodeSync/CodeSync/docs/decisions.md)**
  - Summary of core architectural design decisions (tech stacks, database engines, extension architectures) with context, alternatives considered, and consequences.

---

## Onboarding Quick Start

1. Set up your local workspace by following the **[Local Development Guide](file:///d:/CodeSync/CodeSync/docs/local-development.md)**.
2. Read the **[System Architecture Guide](file:///d:/CodeSync/CodeSync/docs/architecture.md)** to understand how the Chrome Extension communicates with the FastAPI Backend.
3. Review the **[Contribution Guidelines](file:///d:/CodeSync/CodeSync/CONTRIBUTING.md)** before writing any code.
