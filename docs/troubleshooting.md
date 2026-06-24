# Troubleshooting Guide

This guide compiles common issues, error messages, and step-by-step resolution paths for developers setting up, testing, or modifying CodeSync.

---

## 1. Authentication & OAuth Issues

### GitHub OAuth Redirect Mismatch (`redirect_uri_mismatch`)
- **Symptom**: Clicking "Login with GitHub" redirects you to a GitHub error page displaying `error: redirect_uri_mismatch`.
- **Root Cause**: The authorization callback URL configured in your GitHub Developer Settings does not match the redirect URL processed by the backend.
- **Resolution**:
  1. Open your [GitHub Developer Settings](https://github.com/settings/developers) and locate your OAuth application.
  2. Verify that the **Authorization callback URL** is set to:
     `http://localhost:8000/api/v1/auth/github/callback`
  3. Ensure that your `backend/.env` file has the correct `FRONTEND_URL` pointing to the extension context:
     `FRONTEND_URL=chrome-extension://<your_extension_id>/options.html`

### GitHub Token Scope & Decryption Issues
- **Symptom**: Repository provisioning crashes with a `404 Not Found` or `403 Forbidden` from GitHub's API, even though the user is authenticated. Alternatively, the backend logs show `cryptography.fernet.InvalidToken`.
- **Root Cause**:
  1. The OAuth app is missing the required `repo` scope, preventing token authorizations from managing repos.
  2. The `ENCRYPTION_KEY` in `backend/.env` was modified or does not match the key used to encrypt the token initially, making decryption fail.
- **Resolution**:
  - Re-authorize the application. Verify that your scopes list inside `GitHubOAuthService.get_authorization_url` includes `scope=repo%20user:email`.
  - If your encryption key was updated, delete your local user records in the database so they can register again with the new key:
    ```sql
    DELETE FROM users;
    ```
  - Generate a valid encryption key in your terminal:
    ```bash
    python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    ```

---

## 2. Backend & Database Issues

### Neon Database Connection Failures
- **Symptom**: FastAPI fails to start, displaying `ConnectionTimeoutError` or `psycopg.OperationalError: server closed the connection unexpectedly`.
- **Root Cause**:
  1. Missing SSL requirement options. Neon Serverless PostgreSQL requires SSL to connect.
  2. SQLAlchemy connection string uses synchronous syntax.
- **Resolution**:
  - Verify your `DATABASE_URL` in `backend/.env` uses `postgresql+psycopg` and requires SSL:
    `DATABASE_URL=postgresql+psycopg://neondb_owner:...@ep-lucky-darkness-atgbtuvy-pooler.c-9.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require`
  - If you encounter connection pool exhaustion, use the connection pooling endpoint hostname (containing `-pooler` in the host name).

### Alembic Migration Conflicts (Multiple Heads)
- **Symptom**: Running `alembic upgrade head` raises `alembic.util.exc.CommandError: Multiple heads are present; please specify the revision`.
- **Root Cause**: Two developers created database migration scripts concurrently, resulting in branching histories in the database revisions.
- **Resolution**:
  1. Inspect the migration heads:
     ```bash
     alembic heads
     ```
  2. Create a merge revision to unite the branches:
     ```bash
     alembic merge -m "merge branching migrations" <revision_id_1> <revision_id_2>
     ```
  3. Apply the migrations again:
     ```bash
     alembic upgrade head
     ```

### Alembic Enum Creation Failures
- **Symptom**: Migrations crash with `ProgrammingError: relation "bootstrapstatus" already exists`.
- **Root Cause**: Alembic's autogenerate tries to execute `CREATE TYPE bootstrapstatus`, which PostgreSQL rejects if the type was already created.
- **Resolution**:
  - Add `checkfirst=True` to the custom type creation inside your migration scripts:
    ```python
    sa.Enum("pending", "running", "completed", "failed", name="bootstrapstatus").create(op.get_bind(), checkfirst=True)
    ```

---

## 3. Chrome Extension Issues

### Chrome Unpacked Extension Loading Errors
- **Symptom**: Chrome displays errors like `Manifest is not valid` or `Failed to load extension` when loading the unpacked directory.
- **Root Cause**: Spellings or syntax mistakes in `manifest.json`, or registering files that do not exist at the designated paths.
- **Resolution**:
  - Open `manifest.json` and verify the fields are valid JSON (e.g. no trailing commas).
  - Check that the registered content script path exactly matches `content/content_detect.js`.

### LeetCode Selector & Layout Changes
- **Symptom**: LeetCode problem pages open, but the extension toolbar badge remains blank or shows `...` loading status without extracting the title/difficulty.
- **Root Cause**: LeetCode updated its HTML DOM layout, making the current selectors in `content_detect.js` obsolete.
- **Resolution**:
  1. Open Chrome DevTools (`F12`) on the failing LeetCode problem page.
  2. Use the Element Inspector to locate the HTML element containing the problem title and difficulty badge.
  3. Note the CSS class names (e.g. `div.text-title-large`, `span[class*='difficulty']`).
  4. Open [content_detect.js](file:///d:/CodeSync/CodeSync/extension/content/content_detect.js).
  5. Update the selector arrays in `getTitle()` or `getDifficulty()` with the new class names.
  6. Reload the extension in `chrome://extensions/` and reload the LeetCode tab.
