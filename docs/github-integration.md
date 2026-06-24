# GitHub Integration Guide

This guide covers our communication with the GitHub REST API v3, authentication scopes, encrypting/decrypting user tokens, layout bootstrapping, and solution sync commits.

---

## 1. Authentication Scopes & Token Lifecycle

CodeSync requests the following scopes during the GitHub OAuth login process:
- **`repo`**: Grants read/write permissions to public and private user repositories. Required to create repositories, write files, and commit solutions.
- **`user:email`**: Grants read access to the user's email addresses (used to locate the primary email for registration and commit author records).

### Token Security & Cryptography
To prevent token leakages, user tokens are never stored in plaintext:
1. When GitHub returns the access token, the backend encrypts it using **Fernet Symmetric Encryption** (via the `cryptography` library) with a base64-encoded key (`ENCRYPTION_KEY` in `.env`).
2. The encrypted string is persisted in the `github_access_token_encrypted` column of the `users` table.
3. When the backend service needs to invoke GitHub APIs, it decrypts the token temporarily in memory, passes it in the request's Authorization header, and discards it immediately after.

---

## 2. Repository Creation & Provisioning

- **Endpoint**: `POST /repositories/create`
- **Method**: `GitHubRepositoryService.create_github_repository()`
- **Flow**:
  1. Requests a POST call to `https://api.github.com/user/repos` containing `name` and `private`.
  2. If the user is creating a repository that exists, the API returns a `422 Unprocessable Entity`. CodeSync handles this by returning the existing metadata instead of failing.
  3. Returns details including `id` and `full_name`.

---

## 3. Repository Bootstrapping

When a repository is registered, CodeSync async initializes a clean workspace template:
- **Service**: [RepositoryBootstrapService](file:///d:/CodeSync/CodeSync/backend/app/services/repository_bootstrap_service.py)
- **Files Created**:
  1. **`.gitignore`**: Ignores common build/log caches to keep repository directories clean.
  2. **`README.md`**: Created dynamically with the repository name:
     ```markdown
     # {repo_name}
     
     Welcome to my CodeSync solution portfolio!
     
     This repository is automatically managed by CodeSync to log resolved algorithm submissions.
     
     - Repository Bootstrap Version: 1.1
     ```
  3. **`metadata/config.json`**: Persists layout version and roadmap parameters:
     ```json
     {
       "bootstrap_version": "1.1",
       "bootstrapped_at": "...",
       "platforms": {
         "leetcode": true,
         "hackerrank": false,
         "codeforces": false,
         "geeksforgeeks": false
       }
     }
     ```

---

## 4. GitHub Contents API (Idempotent Commits)

We communicate with the Contents endpoint:
`PUT https://api.github.com/repos/{owner}/{repo}/contents/{path}`

### Idempotency Check:
GitHub's Contents API requires a file's **SHA string** if you are updating an existing file. If you do not provide it, the request fails with a `409 Conflict` (meaning the file already exists).
CodeSync ensures idempotent writes via `GitHubContentService.check_file_exists()`:
1. Calls `GET https://api.github.com/repos/{owner}/{repo}/contents/{path}`.
2. If the response returns `200 OK`, it extracts the `sha` value.
3. If it returns `404 Not Found`, the SHA is set to `None`.
4. When calling the `PUT` endpoint, the `sha` parameter is attached iff it was found. This automatically transitions the action from **Create** to **Update** without error.

---

## 5. Network & API Error Handling

GitHub API calls use the asynchronous `httpx` client. We catch and map error conditions:
- **`403 Forbidden` / Rate Limit**: Triggers an `HTTPException(403)` indicating rate limits were exceeded or permissions were blocked.
- **Connection timeouts**: Handled via `httpx.AsyncClient(timeout=10.0)`. Timeout exceptions raise a `502 Bad Gateway` telling the client that GitHub servers were unreachable.
