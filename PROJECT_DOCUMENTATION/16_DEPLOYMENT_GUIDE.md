# Deployment Guide

Deploying ToxiChat Pro requires orchestrating Python (Backend), Node.js (Frontend), MongoDB, and Redis. Below is the standard operating procedure for a Dockerized production deployment.

## Prerequisites
- A Linux host (Ubuntu 22.04 LTS recommended) with at least 16GB RAM (32GB+ if running ML models locally).
- NVIDIA GPU with CUDA drivers installed (Optional, but highly recommended for `faster-whisper` and `onnxruntime-gpu`).
- Docker and Docker Compose installed.

## 1. Environment Configuration

1. Clone the repository to the production server.
2. Create a `.env` file in the `backend/` directory:
```env
# Database
MONGO_URL=mongodb+srv://admin:secure_password@cluster0.mongodb.net/toxichat?retryWrites=true&w=majority
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=generate_a_cryptographically_secure_random_string_here
TOKEN_EXPIRE_HOURS=24
ADMIN_USERNAMES=admin,compliance_officer

# CORS
CORS_ORIGINS=https://chat.yourdomain.com

# AI / ML
HF_TOKEN=your_huggingface_token_here (If using private models)
```

## 2. Infrastructure Setup (Docker Compose)

Create a `docker-compose.yml` in the project root:

```yaml
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: always

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - MONGO_URL=${MONGO_URL}
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - redis
    restart: always
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    restart: always
```

## 3. Building the Containers

### Backend Dockerfile (`backend/Dockerfile`)
Ensure the backend Dockerfile installs system-level dependencies for audio and vision:
```dockerfile
FROM python:3.10-slim
RUN apt-get update && apt-get install -y ffmpeg libsm6 libxext6 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Frontend Dockerfile (`frontend/Dockerfile`)
The frontend should be built statically and served via NGINX.
```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
# Copy custom nginx.conf if routing /api to the backend container
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 4. Execution & Verification
1. Run `docker-compose up -d --build`.
2. Monitor the backend logs: `docker-compose logs -f backend`. Ensure the PyTorch models download successfully on the first boot.
3. Access `http://your-server-ip` and register a new user using one of the usernames defined in `ADMIN_USERNAMES`.
4. Verify the WebSocket connects (Network Tab -> WS).
5. Open the Admin Dashboard and verify telemetry is flowing.
