# CodeSync Project Context

## Current Phase

Phase 1 - MVP Development

---

## Current Objective

Build a Chrome Extension that automatically pushes accepted LeetCode submissions to GitHub.

---

## Architecture

Chrome Extension
    ↓
GitHub OAuth
    ↓
FastAPI Backend
    ↓
GitHub API

---

## Tech Stack

Frontend:
- React
- TypeScript
- Vite
- Chrome Extension Manifest V3

Backend:
- FastAPI
- PostgreSQL
- SQLAlchemy

Authentication:
- GitHub OAuth
- JWT

Deployment:
- Render
- Neon

---

## Decisions Made

### Repository Structure

DSA-Solutions/

└── LeetCode/

    └── {problem_number}_{problem_name}/

### Authentication

GitHub OAuth

### Supported Platform

LeetCode only

### Storage

Backend stores GitHub access token securely.

Extension stores JWT only.

---

## Discovery Findings

LeetCode:

✓ Accepted status detectable

✓ Problem title extractable

✓ Difficulty extractable

✓ Topics extractable

✓ Code extractable

✓ Runtime extractable

✓ Memory extractable

GraphQL investigation for full problem description postponed.

---

## Current Status

Completed:

- Product idea finalized
- MVP scope finalized
- Repository structure finalized
- Authentication strategy finalized
- LeetCode feasibility validated

In Progress:

- Backend setup

Pending:

- FastAPI scaffold
- GitHub OAuth
- Extension scaffold
- JWT authentication
- LeetCode content script
- GitHub upload service

---

## Next Milestone

Implement GitHub OAuth backend.