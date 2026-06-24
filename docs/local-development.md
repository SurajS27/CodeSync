# Local Development Guide

This guide walks you through setting up your local environment to run, test, and contribute to both the backend service and the Chrome extension.

---

## 1. Prerequisites

Ensure you have the following installed on your machine:
- **Python**: Version `3.14.x` (or newer).
- **Google Chrome**: Needed to run and debug Manifest V3 extensions.
- **Git**: For version control.
- **PostgreSQL Client (Optional)**: If you want to connect to the Neon database via command line.

---

## 2. Backend Environment Setup

### 1. Clone & Navigate
```bash
git clone https://github.com/SurajS27/CodeSync.git
cd CodeSync/backend
```

### 2. Configure Virtual Environment
Create and activate a python virtual environment:

On Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\activate
```

On macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 3. Environment Variables Configuration

Create a file named `.env` in the `backend/` directory by copying `.env.example`:

```bash
cp .env.example .env
```

Modify `backend/.env` with the following variables:

```ini
# General app configuration
ENV=development
LOG_LEVEL=DEBUG
SECRET_KEY=generate_a_secure_hex_key_32_chars_or_more

# Database Connection (Async Psycopg driver syntax)
DATABASE_URL=postgresql+psycopg://username:password@hostname:5432/dbname?sslmode=require

# Cryptography Fernet Key (for encryption of oauth tokens)
ENCRYPTION_KEY=your_base64_fernet_key_here

# GitHub Application OAuth Integration (replace with keys from settings/developers)
GITHUB_CLIENT_ID=your_oauth_client_id
GITHUB_CLIENT_SECRET=your_oauth_client_secret

# Local Target Redirect
FRONTEND_URL=chrome-extension://mock_chrome_extension_id/options.html
```

---

## 4. Database Migrations (Alembic)

Once your `.env` contains a valid `DATABASE_URL` mapping to a Neon PostgreSQL instance, initialize table schemas using Alembic:

```bash
# Verify you are at database head revision
alembic current

# Run all migrations up to head
alembic upgrade head
```

If you modify models in `app/models/`, run autogenerate to create new schema files:
```bash
alembic revision --autogenerate -m "add index to sync status"
alembic upgrade head
```

---

## 5. Startup the Backend API
Run the local development server:

```bash
python -m uvicorn app.main:app --reload
```
The application will boot at `http://127.0.0.1:8000`. You can test endpoints via Swagger UI at `http://127.0.0.1:8000/docs`.

---

## 6. Chrome Extension Setup

1. Open Google Chrome and type `chrome://extensions/` in the address bar.
2. In the top-right corner, toggle **Developer mode** to **ON**.
3. In the top-left, click the **Load unpacked** button.
4. Select the `extension/` folder located in your repository root (`CodeSync/extension`).
5. The extension will load as **CodeSync** and display its icon in the browser header toolbar.

---

## 7. Troubleshooting Tips

### 1. ValidationError for Settings
If FastAPI crashes with validation errors (e.g. `Field required [type=missing, ...]`), it means your `backend/.env` file is missing, located in the wrong directory, or missing required fields. Ensure your terminal's working directory is `backend` when running uvicorn.

### 2. Alembic Enum Type Exists Error
If Alembic fails on `upgrade head` with `enum type bootstrapstatus already exists`, open the failing migration file and make sure the enum type creation includes `checkfirst=True` or is skipped manually. E.g.:
```python
# Create enum with existence checks
bootstrap_status_enum = sa.Enum("pending", "running", "completed", "failed", name="bootstrapstatus")
bootstrap_status_enum.create(op.get_bind(), checkfirst=True)
```

### 3. Extension Fails to Detect LeetCode Problems
If the badge (`E`, `M`, `H`) is missing on LeetCode:
1. Make sure you are on a problem page path (e.g. `https://leetcode.com/problems/two-sum/`).
2. Refresh the LeetCode tab to force content script injection.
3. Open `chrome://extensions/`, click **Reload** on the CodeSync card, and reload the tab again.
