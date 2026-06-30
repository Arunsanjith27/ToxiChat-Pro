# ToxiChat — AI-Powered Toxicity Prediction Platform

Production-ready real-time chat with ML toxicity detection, conversation escalation prediction, JWT authentication, admin moderation, and analytics.

![ToxiChat](https://img.shields.io/badge/ToxiChat-v3.0-emerald)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)
![React](https://img.shields.io/badge/Frontend-React-61DAFB)

## Features

- **JWT Authentication** — Register, login, forgot/reset password, protected routes
- **Real-time WebSocket Chat** — Typing indicators, online status, delivered/seen ticks
- **AI Toxicity Detection** — HuggingFace Transformers → scikit-learn → keyword fallback
- **Pre-send Warning Popup** — Review toxic messages before sending with rewrite suggestions
- **Conversation Escalation Prediction** — Health scores and trend analysis per chat
- **User Reputation Scores** — Dynamic scoring based on message history
- **Analytics Dashboard** — Toxicity trends, conversation health, flagged content
- **Admin Moderation Panel** — Flagged messages, user management, mute/unmute
- **Profile Management** — Display name, bio, avatar upload
- **Dark / Light Mode** — Theme toggle with persistent preference
- **Docker Ready** — Full stack with MongoDB, Redis, frontend nginx

## Architecture

```mermaid
flowchart TB
    subgraph Client
        FE[React SPA]
        WS[WebSocket Client]
    end

    subgraph Backend
        API[FastAPI REST]
        WSS[WebSocket Handler]
        ML[ML Service]
        ESC[Escalation Engine]
        AUTH[JWT Auth]
    end

    subgraph Data
        MONGO[(MongoDB Atlas)]
        REDIS[(Redis)]
    end

    FE -->|HTTPS + JWT| API
    WS -->|/ws/token| WSS
    API --> AUTH
    WSS --> ML
    WSS --> ESC
    API --> MONGO
    WSS --> MONGO
    WSS --> REDIS
    ML -->|toxic-bert| HF[HuggingFace Models]
```

## Project Structure

```
toxichat/
├── backend/
│   ├── main.py              # FastAPI app (REST + WebSocket)
│   ├── auth.py              # JWT dependencies
│   ├── database.py          # MongoDB + in-memory fallback
│   ├── ml_service.py        # Toxicity detection
│   ├── escalation.py        # Conversation escalation + reputation
│   ├── models.py            # Pydantic schemas
│   ├── security.py          # Password hashing, sanitization
│   ├── redis_service.py     # Cache, presence, rate limiting
│   ├── tests/               # pytest suite
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # React UI components
│   │   ├── context/         # Auth + Theme providers
│   │   └── services/        # API client layer
│   ├── Dockerfile
│   └── nginx.conf
├── models/                  # Optional sklearn .pkl files
├── docker-compose.yml
├── render.yaml              # Render deployment
└── vercel.json              # Vercel frontend deployment
```

## Quick Start (Local)

### Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB (optional — falls back to in-memory)
- Redis (optional — falls back to in-memory)

### 1. Backend

```bash
cd backend
cp .env.example .env
pip install -r requirements.txt
python main.py
```

API runs at `http://localhost:8000`

### 2. Frontend

```bash
cd frontend
cp .env.example .env.local
npm install
npm start
```

App runs at `http://localhost:3000`

### 3. Docker (Full Stack)

```bash
cp .env.example .env
docker-compose up --build
```

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- MongoDB: `localhost:27017`
- Redis: `localhost:6379`

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing key | (change in prod!) |
| `MONGO_URL` | MongoDB connection string | `mongodb://localhost:27017` |
| `DB_NAME` | Database name | `toxichat` |
| `REDIS_URL` | Redis connection | `redis://localhost:6379` |
| `CORS_ORIGINS` | Allowed origins (comma-separated) | `*` |
| `ADMIN_USERNAMES` | Admin usernames (comma-separated) | `admin` |
| `REACT_APP_API_URL` | Frontend API base URL | `http://localhost:8000` |

## API Documentation

### Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/register` | No | Register new user |
| POST | `/api/login` | No | Login, returns JWT |
| POST | `/api/auth/forgot-password` | No | Generate reset token |
| POST | `/api/auth/reset-password` | No | Reset password with token |
| GET | `/api/me` | JWT | Current user profile |

### Chat & ML

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/users` | JWT | List users |
| GET | `/api/messages/{u1}/{u2}` | JWT | Chat history |
| POST | `/api/predict` | JWT | Toxicity prediction |
| POST | `/api/predict/escalation` | JWT | Escalation + health |
| POST | `/api/rewrite` | JWT | Toxic text rewrite |
| GET | `/api/conversation/health/{partner}` | JWT | Conversation health |
| GET | `/api/search?q=` | JWT | Search messages |

### Dashboard & Admin

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/dashboard/stats` | JWT | Analytics data |
| GET | `/api/admin/flagged` | Admin | Flagged messages |
| GET | `/api/admin/users` | Admin | All users |
| POST | `/api/admin/action` | Admin | Moderation actions |

### WebSocket

Connect: `ws://host/ws/{jwt_token}`

**Send:**
```json
{"type": "message", "text": "Hello", "receiver": "username", "force_send": false}
{"type": "typing", "receiver": "username"}
{"type": "seen", "id": "msg_id", "sender": "username"}
```

**Receive:** `message`, `toxicity_pre_send`, `toxicity_alert`, `toxicity_warning`, `typing`, `status_update`, `users_list`, `system`

## ML Model Setup

Place optional sklearn models in `models/`:
- `model.pkl` — Trained classifier
- `tfidf_vectorizer.pkl` — TF-IDF vectorizer

Without these, the app uses HuggingFace `unitary/toxic-bert` or keyword fallback.

## Deployment

### MongoDB Atlas

1. Create a free cluster at [mongodb.com/atlas](https://www.mongodb.com/atlas)
2. Get connection string: `mongodb+srv://user:pass@cluster.mongodb.net/toxichat`
3. Set `MONGO_URL` in backend environment

### Render (Backend)

1. Connect GitHub repo to Render
2. Use `render.yaml` or create Web Service with Docker
3. Set environment variables (`MONGO_URL`, `SECRET_KEY`, `CORS_ORIGINS`)
4. Deploy — health check at `/`

### Vercel (Frontend)

```bash
cd frontend
npm run build
vercel --prod
```

Set `REACT_APP_API_URL` to your Render backend URL.

### Deployment Checklist

- [ ] Generate strong `SECRET_KEY` (32+ random chars)
- [ ] Configure MongoDB Atlas with IP whitelist
- [ ] Set `CORS_ORIGINS` to your frontend domain
- [ ] Set `ADMIN_USERNAMES` for admin access
- [ ] Configure `REACT_APP_API_URL` on frontend
- [ ] Enable HTTPS on both frontend and backend
- [ ] Test WebSocket connectivity through proxy
- [ ] Run `pytest` in backend before deploy
- [ ] Run `npm run build` in frontend before deploy
- [ ] Set up MongoDB backups
- [ ] Monitor `/` health endpoint

## Testing

```bash
cd backend
pip install -r requirements.txt
pytest -v
```

```bash
cd frontend
npm run build
```

## Screenshots

> Add screenshots of Login, Chat, Pre-send Warning, Analytics Dashboard, and Admin Panel after deployment.

## License

MIT
