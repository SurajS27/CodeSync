# CodeSync API Endpoint Specifications

All endpoints are prefixed with `/api/v1` and communicate using JSON payloads.

---

## 1. Authentication Endpoints

### GET `/auth/github/login`
- **Purpose**: Generates the GitHub OAuth authorization page URL.
- **Authentication**: None.
- **Response (200 OK)**:
  ```json
  {
    "authorization_url": "https://github.com/login/oauth/authorize?client_id=...",
    "state": "anti_csrf_random_string"
  }
  ```

---

### GET `/auth/github/callback`
- **Purpose**: Callback endpoint for GitHub OAuth redirects. Exchanges authorization code for an access token, decrypts profile, and issues CodeSync JWT.
- **Authentication**: None.
- **Request Parameters**:
  - `code` (string, query): Temporary code issued by GitHub.
  - `state` (string, query): Anti-forgery verification token.
- **Response (200 OK)**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
    "token_type": "bearer",
    "user": {
      "github_id": "91777325",
      "github_username": "SurajS27",
      "github_email": "user@codesync.dev",
      "github_avatar_url": "https://avatars.githubusercontent.com/u/91777325",
      "is_active": true,
      "id": "febc0596-dfa4-43e7-99ba-60e78db163ec"
    }
  }
  ```
- **Error Responses**:
  - `400 Bad Request`: If OAuth state verification checks fail or code exchange fails.

---

### GET `/auth/me`
- **Purpose**: Returns the logged-in user profile details.
- **Authentication**: JWT Bearer Token (`Authorization: Bearer <token>`).
- **Response (200 OK)**:
  ```json
  {
    "github_id": "91777325",
    "github_username": "SurajS27",
    "github_email": "user@codesync.dev",
    "github_avatar_url": "https://avatars.githubusercontent.com/u/91777325",
    "is_active": true,
    "id": "febc0596-dfa4-43e7-99ba-60e78db163ec",
    "created_at": "2026-06-24T08:58:19Z",
    "updated_at": "2026-06-24T11:47:46Z"
  }
  ```
- **Error Responses**:
  - `401 Unauthorized`: Invalid/missing token.

---

### POST `/auth/logout`
- **Purpose**: Signs user out.
- **Authentication**: JWT Bearer Token.
- **Response (200 OK)**:
  ```json
  {
    "message": "Logged out successfully."
  }
  ```

---

## 2. Repository Endpoints

### POST `/repositories/create`
- **Purpose**: Provisions a repository on GitHub (creates if missing) and triggers bootstrapping.
- **Authentication**: JWT Bearer Token.
- **Request Body**:
  ```json
  {
    "repo_name": "CodeSync_try",
    "is_private": true
  }
  ```
- **Response (201 Created)**:
  ```json
  {
    "repository": {
      "id": "3a7b5c8d-12ef-3456-789a-0123456789ab",
      "repo_name": "CodeSync_try",
      "repo_full_name": "SurajS27/CodeSync_try",
      "bootstrap_status": "completed",
      "bootstrapped_at": "2026-06-24T12:00:15Z"
    },
    "bootstrap_status": "completed",
    "message": "Repository provisioned and bootstrapped successfully."
  }
  ```

---

### GET `/repositories`
- **Purpose**: Retrieves all provisioned repositories owned by the user.
- **Authentication**: JWT Bearer Token.
- **Response (200 OK)**:
  ```json
  [
    {
      "id": "3a7b5c8d-12ef-3456-789a-0123456789ab",
      "repo_name": "CodeSync_try",
      "repo_full_name": "SurajS27/CodeSync_try",
      "bootstrap_status": "completed",
      "bootstrapped_at": "2026-06-24T12:00:15Z"
    }
  ]
  ```

---

### GET `/repositories/{repository_id}`
- **Purpose**: Retrieves details for a specific repository.
- **Authentication**: JWT Bearer Token.
- **Response (200 OK)**:
  ```json
  {
    "id": "3a7b5c8d-12ef-3456-789a-0123456789ab",
    "repo_name": "CodeSync_try",
    "repo_full_name": "SurajS27/CodeSync_try",
    "bootstrap_status": "completed",
    "bootstrapped_at": "2026-06-24T12:00:15Z"
  }
  ```
- **Error Responses**:
  - `404 Not Found`: Repository not found or doesn't exist.
  - `403 Forbidden`: User does not own the requested repository.

---

## 3. Challenge Sync Endpoints

### POST `/sync/leetcode`
- **Purpose**: Commits a solved challenge to the repository and logs history.
- **Authentication**: JWT Bearer Token.
- **Request Body**:
  ```json
  {
    "repository_id": "3a7b5c8d-12ef-3456-789a-0123456789ab",
    "problem_title": "Two Sum",
    "problem_slug": "two-sum",
    "difficulty": "easy",
    "language": "python",
    "source_code": "class Solution:\n    def twoSum(self, nums: List[int], target: int) -> List[int]:\n        ..."
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "sync_id": "8a9b0c1d-23ef-4567-89ab-0123456789cd",
    "status": "completed",
    "commit_sha": "d3130cd3c8e8a119e18...a9f",
    "commit_url": "https://github.com/SurajS27/CodeSync_try/commit/d3130cd3...",
    "repository_path": "leetcode/easy/two-sum/",
    "github_file_path": "leetcode/easy/two-sum/solution.py",
    "error_message": null
  }
  ```
- **Error Responses**:
  - `400 Bad Request`: Unsupported programming language.
  - `403 Forbidden`: User does not own the target repository.
  - `409 Conflict`: Unique constraint violation (this problem-language combination is already synced).
  - `502 Bad Gateway`: GitHub API write error.

---

### GET `/sync/history`
- **Purpose**: Lists user sync log history, ordered by creation date descending.
- **Authentication**: JWT Bearer Token.
- **Response (200 OK)**:
  ```json
  [
    {
      "id": "8a9b0c1d-23ef-4567-89ab-0123456789cd",
      "user_id": "febc0596-dfa4-43e7-99ba-60e78db163ec",
      "repository_id": "3a7b5c8d-12ef-3456-789a-0123456789ab",
      "platform": "leetcode",
      "problem_title": "Two Sum",
      "problem_slug": "two-sum",
      "difficulty": "easy",
      "language": "python",
      "repository_path": "leetcode/easy/two-sum/",
      "commit_sha": "d3130cd3c8e8a119e18...a9f",
      "commit_url": "https://github.com/SurajS27/CodeSync_try/commit/d3130cd3...",
      "sync_status": "completed",
      "github_file_path": "leetcode/easy/two-sum/solution.py",
      "error_message": null,
      "created_at": "2026-06-24T12:15:30Z",
      "updated_at": "2026-06-24T12:15:32Z"
    }
  ]
  ```
