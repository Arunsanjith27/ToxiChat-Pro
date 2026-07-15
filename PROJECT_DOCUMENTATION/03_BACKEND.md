# Backend Architecture

ToxiChat Pro utilizes **FastAPI** as its core backend framework to provide asynchronous, high-throughput REST and WebSocket APIs. The entry point for the application is `main.py`.

## Core Structure
- **FastAPI App (`main.py`)**: Defines routers, middlewares, connection lifespan (startup/shutdown hooks), and the main entry points for AI endpoints.
- **Authentication (`auth.py`)**: Manages JWT encoding/decoding, stateless session tracking, and Role-Based Access Control (RBAC).
- **Security (`security.py`)**: Handles password hashing (`bcrypt`), input sanitization (preventing XSS payload injections into chat), and file validation for uploads.
- **Database (`database.py`)**: Asynchronous Motor client for MongoDB, abstracting CRUD operations behind awaitable helpers.

## Security & Middleware
1. **SecurityHeadersMiddleware**: A custom Starlette `BaseHTTPMiddleware` that intercepts outgoing HTTP responses and injects strict security headers:
   - `Strict-Transport-Security: max-age=31536000; includeSubDomains`
   - `X-Content-Type-Options: nosniff`
   - `X-Frame-Options: DENY`
   - `X-XSS-Protection: 1; mode=block`
2. **CORS Middleware**: Pre-configured to dynamically load from `.env` (`CORS_ORIGINS`) to permit external frontend connections securely.
3. **Authentication**: Uses `HTTPBearer` for standard `Authorization: Bearer <token>` flows.

## Role-Based Access Control (RBAC)
- Dependency injection (`Depends(get_current_user)`) secures endpoints.
- `Depends(require_admin)` is used for privileged endpoints. A user is an admin if their username matches the comma-separated `ADMIN_USERNAMES` environment variable or if their MongoDB document possesses `"role": "admin"`.

## Background & Auxiliary Services

### 1. Audit Engine (`audit.py`)
Provides an asynchronous, non-blocking ledger for critical actions (logins, logouts, administrative overrides, incident escalations). Uses MongoDB insertions to store the `actor_username`, `action`, `resource_type`, and timestamp for the compliance dashboard.

### 2. Incident Engine (`incidents.py`)
Orchestrates the creation and resolution of "Incidents". When a conversation escalates to `CRITICAL`, it automatically calls `incidents.create_incident()`. This captures a point-in-time snapshot of the conversation, utilizing `copilot_context.py` to recursively extract flagged reasons and summarize the timeline for HR/Legal review.

### 3. Report Builder (`report_builder.py` & `generate_report.py`)
Provides automated compliance reporting. Generates structured JSON dictionaries representing an incident, which are then either rendered on the frontend or piped into a PDF generator via `test_pdf.py` logic.

### 4. Compliance & Policy (`compliance.py`)
Handles data retention policies, redaction of specific messages (GDPR right to be forgotten), and audit trail extraction.

### 5. Redis Service (`redis_service.py`)
Initializes an `aioredis` pool. Primarily used as a Pub/Sub backbone to coordinate WebSocket broadcasts across multiple Uvicorn worker instances.

### 6. Presence Tracker (`presence.py`)
Provides real-time hooks into the WebSocket `connect`/`disconnect` lifecycle to update MongoDB's `is_online` status, powering the "Online" indicators on the frontend.

## API Routers
- **Auth Router (`routers/auth_router.py`)**: Handles `/api/auth/register`, `/api/auth/login`, and `/api/auth/reset` endpoints.
- **Main Router (`main.py`)**: Handles the AI logic (`/api/predict`, `/api/image/analyze`, `/api/audio/analyze`), WebSockets (`/ws/{username}`), and administrative commands.
