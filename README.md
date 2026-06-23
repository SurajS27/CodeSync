# CodeSync 🚀

CodeSync is a Chrome Extension that automatically syncs accepted coding challenge submissions from platforms like LeetCode to GitHub.

The goal is to help developers build and maintain a coding portfolio without manually copying solutions into repositories.

---

# Problem Statement

Developers solve hundreds of coding problems across different platforms but rarely maintain a structured record of their solutions.

As a result:

- GitHub activity remains disconnected from coding practice.
- Solutions are scattered across multiple platforms.
- Building a public coding portfolio requires manual effort.
- Progress tracking becomes difficult.

CodeSync automates this entire workflow.

---

# MVP Features

## GitHub Authentication

- GitHub OAuth Login
- Secure JWT-based authentication
- Repository configuration

## LeetCode Integration

- Detect Accepted submissions
- Extract problem metadata
- Extract submitted solution
- Generate problem documentation

## GitHub Synchronization

Automatically create:

```text
DSA-Solutions/
└── LeetCode/
    └── 28_Find_the_Index_of_the_First_Occurrence_in_a_String/
        ├── solution.cpp
        └── README.md
```

and push the files to GitHub.

---

# Example Generated README

```markdown
# 28. Find the Index of the First Occurrence in a String

## Platform
LeetCode

## Difficulty
Easy

## Topics
- String
- Two Pointers

## Runtime
0 ms

## Memory
8.94 MB

## Language
C++

## Problem URL
https://leetcode.com/problems/find-the-index-of-the-first-occurrence-in-a-string/
```

---

# Architecture

```text
Chrome Extension
        │
        ▼
GitHub OAuth
        │
        ▼
FastAPI Backend
        │
        ▼
PostgreSQL
        │
        ▼
GitHub API
```

---

# Tech Stack

## Chrome Extension

- React
- TypeScript
- Vite
- Manifest V3

## Backend

- FastAPI
- SQLAlchemy 2.x
- PostgreSQL
- Alembic
- Pydantic v2

## Authentication

- GitHub OAuth
- JWT

## Database

- PostgreSQL
- Neon (Planned Deployment)

## Deployment

- Render
- Neon PostgreSQL

---

# Repository Structure

```text
CodeSync/
│
├── backend/
│
├── extension/
│
├── docs/
│   ├── mvp.md
│   └── project_context.md
│
└── README.md
```

---

# Development Roadmap

## Phase 1 — MVP

### Backend

- [ ] FastAPI Foundation
- [ ] PostgreSQL Integration
- [ ] Alembic Setup
- [ ] User Model
- [ ] GitHub OAuth
- [ ] JWT Authentication

### Extension

- [ ] Manifest V3 Setup
- [ ] React + TypeScript Setup
- [ ] Settings Page
- [ ] OAuth Integration

### LeetCode Integration

- [ ] Accepted Submission Detection
- [ ] Metadata Extraction
- [ ] Solution Extraction

### GitHub Sync

- [ ] Repository Creation
- [ ] File Upload
- [ ] README Generation

---

## Phase 2 — Platform Support

- HackerRank
- Codeforces
- GeeksForGeeks
- AtCoder

---

## Phase 3 — Analytics

- Coding Streaks
- Difficulty Analysis
- Topic Distribution
- Progress Dashboard

---

## Phase 4 — Data Engineering

- Event Pipelines
- Daily Aggregations
- Trend Analysis
- Recommendation Engine

---

## Phase 5 — Intelligence Layer

- Personalized Recommendations
- Weak Topic Detection
- Interview Preparation Insights
- Learning Paths

---

# Current Status

🚧 In Development

Current Milestone:

- Backend Foundation
- Database Setup
- GitHub OAuth

---

# License

MIT License

---

# Author

**Suraj Sikchi**

Building tools that help developers learn, track progress, and showcase their coding journey.