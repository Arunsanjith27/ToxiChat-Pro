# Security Audit & Posture

ToxiChat handles highly sensitive compliance data, PII, and potentially illegal conversational content. As such, its security posture is aggressive.

## 1. Authentication & Authorization (RBAC)
- **JWT Standard**: Utilizes `HS256` signed JSON Web Tokens with a 24-hour expiration (`TOKEN_EXPIRE_HOURS`).
- **Stateless Verification**: Tokens are verified purely by cryptographic signature (`auth.py: decode_token`).
- **Role-Based Access Control**: `Depends(require_admin)` guards all incident, audit, and deep AI endpoints. A user is an admin if their username exists in the `ADMIN_USERNAMES` `.env` variable, or if their MongoDB document contains `"role": "admin"`.

## 2. Brute-Force & Denial of Service Protection
- **Rate Limiting**: A Redis-backed rate limiter (`redis_service.increment_rate`) tracks IP addresses and Usernames.
  - Global APIs limit requests to 30 per minute (`GLOBAL_RATE_LIMIT`).
  - WebSockets throttle messages aggressively (`RATE_LIMIT_MSG = 30`).
- **Account Lockouts**: `routers/auth_router.py` implements a 15-minute lockout (`LOCKOUT_WINDOW = 900`) if a username experiences 5 failed login attempts (`MAX_LOGIN_ATTEMPTS`). This prevents credential stuffing.

## 3. Data Sanitization & Injection Prevention
- **MongoDB Protection**: Utilizing `motor` abstracts away string concatenation, fundamentally preventing NoSQL injection attacks.
- **XSS Prevention**: 
  - `security.sanitize_input()` strips malicious tags from incoming messages before they hit MongoDB or AI pipelines.
  - React's innate DOM escaping prevents rendering `<script>` tags on the frontend, even if they bypass the backend sanitization layer.

## 4. Middleware & HTTP Security
The backend injects strict security headers on every response via `SecurityHeadersMiddleware`:
- `Strict-Transport-Security: max-age=31536000; includeSubDomains` (Forces HTTPS).
- `X-Content-Type-Options: nosniff` (Prevents MIME-sniffing drive-by downloads).
- `X-Frame-Options: DENY` (Prevents Clickjacking by disallowing iframe embeds).
- `X-XSS-Protection: 1; mode=block` (Legacy browser XSS mitigation).

## 5. File Upload Vulnerabilities
- `api/profile/avatar`, `api/image/analyze`, and `api/audio/analyze` endpoints accept `multipart/form-data`.
- **Mitigation**: `security.validate_file()` enforces a strict 10MB size limit. The backend relies on standard library implementations (e.g., `python-multipart`, `pydub`, `PIL`) to parse headers, and re-encodes/hashes the files rather than blindly serving uploaded binaries.

## 6. Known Security Risks (Accepted)
- **Secret Key Exposure**: The `SECRET_KEY` defaults to `"toxichat-secret-key-change-in-prod"` if not provided in the `.env` file. A failure to provision environment variables will result in easily forged JWTs.
- **In-Memory Fallback Lack of Auth**: If MongoDB fails and the system boots into `_use_memory = True` mode, the database starts empty. The first user to register effectively has zero reputation history, and if `ADMIN_USERNAMES` isn't set, administration is impossible.
