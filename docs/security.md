# CodeSync Security Guidelines

This document details the security model, encryption mechanics, access controls, and data storage protections implemented across the CodeSync project.

---

## 1. Authentication & JWT Security

- **Mechanism**: CodeSync uses JSON Web Tokens (JWT) to secure access to backend endpoints.
- **Algorithm**: tokens are signed using the `HS256` symmetric signing algorithm.
- **Expiration**: Access tokens are configured with a default expiration lifespan of 24 hours (1440 minutes).
- **Payload**: The token payload contains:
  - `sub`: The unique database UUID of the User.
  - `github_id`: The user's GitHub profile ID.
  - `exp`: Expiration timestamp.
- **Validation**: Incoming HTTP requests are intercepted by FastAPI's dependency injection layer (`Depends(get_current_user)`). The backend decodes the signature, validates expiration states, loads user records from PostgreSQL, and rejects invalid queries with an `HTTP 401 Unauthorized`.

---

## 2. GitHub Token Encryption at Rest

To secure developer credentials, user access tokens are encrypted before being written to PostgreSQL:
- **Encryption Algorithm**: **AES-128/256 in CBC mode** via the cryptography library's **Fernet** utility.
- **Secret Key**: Configured using a 32-byte URL-safe base64-encoded key (`ENCRYPTION_KEY` in `.env`).
- **Scope Limits**: Encrypted tokens are only loaded in memory temporarily when making calls to GitHub APIs. They are never returned in client response JSONs.

---

## 3. Repository Ownership Validation

To prevent malicious access, the backend enforces repository ownership limits on all operations:
- **Enforcement Layer**: [RepositoryAccessService](file:///d:/CodeSync/CodeSync/backend/app/services/repository_access_service.py).
- **Execution Flow**:
  1. For every modify/read request, the backend extracts the `user_id` from the JWT.
  2. Queries the `repositories` table to load the record.
  3. If the repository does not exist, raises an `HTTP 404 Not Found`.
  4. Checks if the repository's `user_id` matches the user UUID. If they mismatch, raises an `HTTP 403 Forbidden` and blocks the transaction.

---

## 4. Extension Storage Security

- **Mechanism**: The Chrome Extension stores credentials locally using the `chrome.storage.local` API.
- **Data Saved**:
  - `token`: CodeSync API JWT token.
  - `user`: Authenticated user profile metadata (username, avatar, email).
  - `selectedRepositoryId`: Active repository UUID.
- **Mitigation**: Storing the backend JWT instead of the GitHub access token in the browser minimizes the attack surface. If the browser storage is compromised, only the CodeSync API JWT is leaked, which expires within 24 hours. The permanent GitHub access token remains encrypted in our database.

---

## 5. Known Limitations & Future Roadmap

### Current Limitations:
- **Plaintext Transmission to Database**: Communication between the backend and Neon PostgreSQL database is secured via SSL (`sslmode=require`), but data inside database pages is not encrypted column-by-column except for the GitHub token.
- **Stateless JWT Revocation**: Current JWTs are stateless. If a token is compromised, it cannot be revoked before it expires.

### Future Security Roadmaps (v1.0+):
- **Token Deny-listing**: Implement a Redis-backed deny-list to revoke compromised JWTs instantly upon logout.
- **IP Rate Limiting**: Configure FastAPI middleware to limit requests from single clients, mitigating brute-force risks on login endpoints.
