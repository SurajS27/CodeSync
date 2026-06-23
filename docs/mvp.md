# CodeSync MVP Specification

## Project Overview

CodeSync is a Chrome Extension that automatically detects accepted coding challenge submissions and pushes them to a GitHub repository.

The primary goal is to help developers automatically maintain their coding portfolio without manual effort.

---

## MVP Goal

When a user gets an Accepted submission on LeetCode:

1. Detect Accepted status
2. Extract problem metadata
3. Extract solution code
4. Generate README.md
5. Push files to GitHub

---

## Supported Platforms

### MVP

- LeetCode

### Future

- HackerRank
- Codeforces
- GeeksForGeeks

---

## Authentication

### MVP

GitHub OAuth

User Flow:

User
→ Connect GitHub
→ Authorize Application
→ JWT Generated
→ Extension Authenticated

---

## Repository Structure

DSA-Solutions/

└── LeetCode/

    └── {problem_number}_{problem_name}/

        ├── solution.cpp

        └── README.md

Example:

DSA-Solutions/

└── LeetCode/

    └── 28_Find_the_Index_of_the_First_Occurrence_in_a_String/

        ├── solution.cpp

        └── README.md

---

## Metadata To Extract

### Required

- Problem Number
- Problem Name
- Difficulty
- Topics
- Runtime
- Memory
- Language
- Solution Code

### Optional

- Full Description
- Examples
- Constraints

---

## README Format

# Problem Name

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

LeetCode URL

---

## Tech Stack

### Extension

- React
- TypeScript
- Vite
- Manifest V3

### Backend

- FastAPI
- SQLAlchemy
- PostgreSQL

### Authentication

- GitHub OAuth
- JWT

### Deployment

- Render
- Neon PostgreSQL

---

## Success Criteria

A user should be able to:

1. Install extension
2. Login with GitHub
3. Submit Accepted solution
4. See solution appear automatically in GitHub repository

without any manual intervention.

---

## Out of Scope For MVP

- Analytics
- Spark
- Airflow
- OpenSearch
- Recommendations
- Dashboard
- Multi-platform support