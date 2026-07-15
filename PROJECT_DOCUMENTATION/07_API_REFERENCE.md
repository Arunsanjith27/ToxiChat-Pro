# API Reference

ToxiChat exposes a suite of REST endpoints primarily defined in `main.py` and `routers/auth_router.py`.

## Authentication APIs

### 1. Register
- **Method:** `POST /api/register`
- **Request Body:** `{ "username": "str", "password": "str", "display_name": "str", "email": "str?" }`
- **Response:** `200 OK` `{ "access_token": "jwt", "username": "str", "role": "user|admin", ... }`
- **Errors:** `400` Username already taken, `429` Rate Limited.

### 2. Login
- **Method:** `POST /api/login`
- **Request Body:** `{ "username": "str", "password": "str" }`
- **Response:** `200 OK` `{ "access_token": "jwt", ... }`
- **Errors:** `401` Invalid username or password, `403` Account locked due to failed attempts.

### 3. Forgot / Reset Password
- **Method:** `POST /api/auth/forgot-password` (Returns mock reset token in dev)
- **Method:** `POST /api/auth/reset-password` (Requires token and `new_password`)

### 4. Logout
- **Method:** `POST /api/logout`
- **Auth Required:** Bearer Token
- **Action:** Sets `is_online: False` and writes to audit log.

## User & Profile APIs

### 1. Get Current User
- **Method:** `GET /api/me`
- **Auth Required:** Bearer Token
- **Response:** Profile object including `reputation_score`, `warnings_count`.

### 2. Update Profile
- **Method:** `PUT /api/profile`
- **Request Body:** `{ "display_name": "str", "bio": "str" }`
- **Auth Required:** Bearer Token

### 3. Upload Avatar
- **Method:** `POST /api/profile/avatar`
- **Auth Required:** Bearer Token
- **Payload:** `multipart/form-data` with `file`.

### 4. List Users (Admin)
- **Method:** `GET /api/users`
- **Auth Required:** Admin Bearer Token

## Core AI & Moderation APIs

### 1. Predict Toxicity (Standard)
- **Method:** `POST /api/predict`
- **Request Body:** `{ "text": "str" }`
- **Response:** Toxicity score, label, PII, Emotion, embedded vector.

### 2. Predict Escalation (Contextual)
- **Method:** `POST /api/predict/escalation`
- **Request Body:** `{ "text": "str", "partner": "username" }`
- **Response:** Appends `escalation` matrix and `conversation_health` by looking up the last 15 messages between the sender and partner in the database.

### 3. Rewrite Message
- **Method:** `POST /api/rewrite`
- **Request Body:** `{ "text": "str" }`
- **Response:** Syntactically neutralized version of the message.

## Multimedia Evidence Pipelines

### 1. Analyze Image
- **Method:** `POST /api/image/analyze`
- **Auth Required:** Admin Bearer Token
- **Payload:** `multipart/form-data` with `file`.
- **Response:** Complex JSON containing `vision` (NSFW scores) and `ocr` (Bounding boxes and extracted text) alongside standard text moderation on the OCR text.

### 2. Analyze Audio
- **Method:** `POST /api/audio/analyze`
- **Auth Required:** Admin Bearer Token
- **Payload:** `multipart/form-data` with `file`.
- **Response:** Audio metadata (duration, sample rate) and `transcript` (timestamped text segments) alongside standard text moderation.

## Conversation Intelligence APIs

### 1. Conversation Summary
- **Method:** `POST /api/conversation/summary`
- **Auth Required:** Bearer Token
- **Request Body:** `{ "conversation_id": "str", "summary_type": "moderator" }`
- **Response:** LLM generated summary string, dominant emotion, and risk level for an entire thread.

### 2. Conversation Prediction (Moderator Copilot)
- **Method:** `GET /api/conversation/prediction/{conversation_id}`
- **Auth Required:** Admin Bearer Token
- **Response:** Hybrid prediction projecting if the conversation will breach the CRITICAL threshold in the near future. Includes historical timeline snapshots.

### 3. Conversation Analytics (Raw Telemetry)
- **Method:** `GET /api/conversation/analytics/{conversation_id}`
- **Response:** Aggregated statistical data (Total toxicity ratio, PII counts, Rewrite acceptance rate) across the thread.

## System APIs

### 1. AI Health
- **Method:** `GET /api/ai/health`
- **Response:** Health status (`ONLINE`, `DEGRADED`) and loaded/unloaded ML modules.

### 2. Search
- **Method:** `GET /api/search?q={query}`
- **Response:** Semantic search results matching the active user's permissions.
