# Testing and Verification Guide

This document describes manual and automated testing scenarios to verify CodeSync integrations and features.

---

## 1. Authentication Integration Test

- **Purpose**: Verify that the GitHub OAuth exchange resolves successfully and yields a valid backend JWT.
- **Steps**:
  1. Open the Chrome Extension popup, click **Login with GitHub**.
  2. A browser tab will open to the authorization URL, redirect to GitHub, and return to the backend callback.
  3. Once redirected to the callback JSON screen, copy the value of `access_token`.
  4. Paste the `access_token` into the **Developer JWT Token** input field in the extension popup and click **Save Dev Token**.
- **Expected Result**: The popup UI immediately updates to show the authenticated profile pane containing your GitHub avatar, username, and email.
- **Failure Cases**:
  - *Bad Request (400)*: Indicates CSRF state parameters mismatch. Close the login tab and retry.
  - *GitHub Connection Error (502)*: Check your internet connection or client ID settings.

---

## 2. Repository Provisioning Test

- **Purpose**: Verify that a repository is created on GitHub, its metadata is saved in Neon DB, and its layout is bootstrapped successfully.
- **Steps**:
  1. Log in to the extension popup or options page.
  2. Open Swagger UI at `http://localhost:8000/docs`.
  3. Click **Authorize** at the top-right and paste the JWT token value.
  4. Under **repositories**, select `POST /api/v1/repositories/create`.
  5. Provide a test repository name:
     ```json
     {
       "repo_name": "CodeSync_Testing",
       "is_private": true
     }
     ```
  6. Execute the request.
- **Expected Result**: Status `201 Created` with a response payload containing repository details showing `bootstrap_status: "completed"`. Check your GitHub account to confirm `CodeSync_Testing` has been created.
- **Failure Cases**:
  - *Invalid Credentials (401)*: Make sure your Bearer token is attached.
  - *GitHub Name Clashes (422)*: Handled gracefully by the backend returning the existing repository details.

---

## 3. Workspace Bootstrapping Test

- **Purpose**: Ensure that the provisioned repository on GitHub receives baseline files correctly.
- **Steps**:
  1. Open the repository created in the previous step on GitHub in your browser.
  2. Inspect the repository root folder.
- **Expected Result**: The repository contains:
  - `.gitignore` (with caches, virtual environment files, and system outputs ignored).
  - `README.md` (displaying custom title `# CodeSync_Testing` and Version 1.1 label).
  - `metadata/config.json` (specifying `"bootstrap_version": "1.1"` and platform booleans).
- **Failure Cases**:
  - *Missing files*: Inspect the `repositories` database table. If `bootstrap_status` is `failed`, review `bootstrap_error` column details to isolate write permission block issues.

---

## 4. LeetCode Detection Test

- **Purpose**: Ensure the extension detects challenge pages and extracts title, slug, and difficulty.
- **Steps**:
  1. Open Google Chrome. Ensure the extension is loaded and active.
  2. Navigate to `https://leetcode.com/problems/two-sum/`.
  3. Look at the CodeSync icon in your browser toolbar.
  4. Open the extension popup.
- **Expected Result**:
  - The toolbar icon shows badge label `E` with a Green background.
  - The extension popup renders:
    - Current Problem: `Two Sum`
    - Difficulty: `Easy` (color-coded green badge)
    - Status: `Ready for Sync`
- **Failure Cases**:
  - *No badge*: Check if you are on a description tab (paths like `/problems/two-sum/submissions/` are ignored). Refresh the page to reload content scripts.

---

## 5. Single Page Application (SPA) Transition Test

- **Purpose**: Verify that LeetCode navigation updates problem state changes in real-time.
- **Steps**:
  1. While on the `Two Sum` page, click on a link to another problem, e.g., `Add Two Numbers`.
  2. Observe the badge and popup UI immediately.
- **Expected Result**:
  - The toolbar badge updates instantly to `M` (Orange).
  - The popup UI dynamically refreshes to show `Add Two Numbers` (Medium) without needing a popup reopen or extension reload.
- **Failure Cases**:
  - *Popup displays outdated information*: Ensure `chrome.storage.onChanged` is registered in `popup.js`.

---

## 6. Challenge Synchronization Test

- **Purpose**: Validate solution commit writes and sync history log records.
- **Steps**:
  1. Use Swagger UI `POST /api/v1/sync/leetcode`.
  2. Provide payload containing a provisioned `repository_id` and test challenge details:
     ```json
     {
       "repository_id": "your-repo-uuid",
       "problem_title": "Two Sum",
       "problem_slug": "two-sum",
       "difficulty": "easy",
       "language": "python",
       "source_code": "print('hello world')"
     }
     ```
  3. Execute the request.
- **Expected Result**:
  - Returns `200 OK` showing `status: "completed"`, `commit_sha`, and `commit_url`.
  - Check your GitHub repository; a new directory structure `leetcode/easy/two-sum/` is created containing `solution.py` and `README.md`.
  - Execute `GET /api/v1/sync/history`. The sync history shows the logged transaction.
- **Failure Cases**:
  - *Duplicate Sync (409)*: Resubmitting the same request yields a Conflict error because of the database unique constraint on repository, slug, and language.
