# CodeSync Contribution Guidelines

Thank you for contributing to CodeSync! To maintain code quality, consistency, and clean project history, please adhere to the following development practices.

---

## Development Workflow

1. **Locate or Create an Issue**: Ensure the feature or bugfix you are working on is documented in an issue tracker.
2. **Branching**: Branch off the main development branch using our branch naming strategy.
3. **Local Setup & Linting**: Set up your local environment as described in the [Local Development Guide](file:///d:/CodeSync/CodeSync/docs/local-development.md). 
4. **Implementation & Tests**: Write clean code, add docstrings, and run manual or automated verification checks before pushing.
5. **Pull Requests**: Open a pull request against the target integration branch. All PRs require at least one reviewer approval and successful test validation.

---

## Branch Naming Strategy

Branches must follow a prefix convention:

- `feat/`: Introducing new features or milestones (e.g. `feat/leetcode-sync-foundation`).
- `fix/`: Resolving bugs, security leaks, or validation gaps (e.g. `fix/jwt-expiration-checks`).
- `docs/`: Writing or revising documentation files (e.g. `docs/api-specifications`).
- `chore/`: Setting up tooling, dependencies, or pipeline configurations (e.g. `chore/add-alembic-indexes`).

---

## Commit Message Convention

We adhere to the conventional commit specification to generate readable change logs automatically:

- **Format**: `<type>(<scope>): <description>`
- **Types**:
  - `feat`: A new feature implementation.
  - `fix`: A bug fix.
  - `docs`: Documentation edits.
  - `style`: Formatter updates, layout styling, missing semicolons (no code changes).
  - `refactor`: Refactoring code without altering external behavior.
  - `test`: Adding or correcting tests.
  - `chore`: Modifying build scripts, environment options, dependencies (no production code changes).

- **Examples**:
  - `feat(sync): implement LeetCode sync orchestration layer`
  - `fix(extension): resolve difficulty badge text parsing error`
  - `docs(db): create database entity relationship diagrams`

---

## Pull Request Process

- Ensure target branches are up to date. Rebase or merge changes from the main development branch before submission.
- Describe what was solved, which files were touched, and link any associated issues.
- Include verification steps (e.g. screenshots of successful sync, console logs, test command runs).

---

## Quality & Code Review Expectations

- **Docstrings & Comments**: Major service functions, database models, and Chrome scripts must include descriptive inline docstrings explaining parameters, logic, and output values. Avoid commenting on obvious lines.
- **Error Handling**: Do not write bare `except:` catch-alls. Catch specific exceptions, log traces with contextual logs, and handle failures gracefully.
- **Idempotency**: All operations (file additions on GitHub, database records) must check states first to prevent duplicate resources or constraints violations.

---

## Testing & Documentation

- Any API modifications require updating [API Reference](file:///d:/CodeSync/CodeSync/docs/api-reference.md).
- Any database model alterations require generating an Alembic migration script and updating [Database Guide](file:///d:/CodeSync/CodeSync/docs/database.md).
- Verify all changes locally before requesting review. Refer to the [Testing Guide](file:///d:/CodeSync/CodeSync/docs/testing.md).
