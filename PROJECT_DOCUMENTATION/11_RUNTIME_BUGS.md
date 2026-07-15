# Runtime Bugs & Edge Cases

This document serves as a post-mortem for recently repaired runtime bugs and a ledger for known edge cases that developers must be aware of when extending the system.

## Recently Repaired Bugs

### 1. Image Evidence Inspector 500 Error (Missing AI Binaries)
- **Symptom**: Uploading an image to `POST /api/image/analyze` resulted in an immediate HTTP 500 Internal Server Error.
- **Root Cause**: The Python environment lacked the `easyocr` and `nudenet` packages. Because the FastAPI error handler wrapped the import/execution error into a generic 500 without printing the stack trace to the frontend, the failure was silent.
- **Resolution**: Installed `easyocr` and `nudenet`. Note: EasyOCR downloads PyTorch weights to `~/.EasyOCR/model` on first run.

### 2. Audio Evidence Inspector 500 Error (Missing Codecs)
- **Symptom**: Uploading a voice note to `POST /api/audio/analyze` failed with a 500.
- **Root Cause**: The `audio_moderation.py` pipeline relies on `faster-whisper` for transcription and `pydub` for audio validation/duration extraction. Both were uninstalled, and `pydub` silently requires system-level `ffmpeg` binaries.
- **Resolution**: Installed `faster-whisper` and `pydub`. 

### 3. Report Generator Unhashable Type Crash
- **Symptom**: Generating a compliance report via `POST /api/reports/generate` crashed the backend event loop with `TypeError: unhashable type: 'list'`.
- **Root Cause**: The `report_builder.py` calls `copilot_context.build_incident_context()`, which aggregates `risk_reasons` across a chat thread. The aggregation logic attempted to deduplicate reasons using a Python `set()`. However, the `risk_engine.py` was generating `risk_reasons` as nested lists (e.g., `[["Toxicity detected"], ["PII detected"]]`). Python sets cannot hash lists.
- **Resolution**: Flattened the `risk_reasons` arrays into strings before attempting set deduplication.

## Known Edge Cases & Limitations

### 1. MongoDB Split-Brain (In-Memory Fallback)
If the MongoDB connection string is invalid at startup, the system gracefully falls back to `_use_memory = True`. 
- **The Danger**: The application appears to function perfectly. Users can register, chat, and generate AI insights. However, all data is stored in a volatile Python dictionary. If the Uvicorn process restarts, all data is irrevocably lost. 
- **Mitigation**: Ensure `MONGO_URL` is tightly monitored.

### 2. WebSocket AI Blocking
The `websocket_endpoint` loop in `main.py` is asynchronous. However, certain ML models (like `easyocr` and some HuggingFace transformers) perform heavy CPU-bound matrix multiplication that does *not* yield to the `asyncio` event loop.
- **The Danger**: If User A sends a long, complex message, the CPU-bound AI processing can block the event loop, causing User B's simple message or typing indicator to experience severe latency spikes.
- **Mitigation**: The `ai.manager` layer must eventually be moved to a Celery/RabbitMQ worker queue running on separate processes (or separate nodes) so that the WebSocket event loop remains strictly non-blocking.

### 3. JWT Expiration vs WebSocket Lifespan
- **The Danger**: WebSockets are validated *only* at the connection handshake in `main.py`. If a user's JWT expires while they maintain an active, unbroken WebSocket connection, the socket remains open and authenticated indefinitely.
- **Mitigation**: Implement a periodic heartbeat that demands re-validation of the JWT signature, or force a socket closure when the token TTL is reached.
