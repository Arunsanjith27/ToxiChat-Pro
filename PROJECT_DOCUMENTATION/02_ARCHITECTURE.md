# System Architecture

ToxiChat Pro is engineered as a **Modular Monolith** designed to handle real-time chat throughput concurrently with heavy Machine Learning inference workloads. 

## Architectural Philosophy
The core principle driving ToxiChat's architecture is **resilient degradation**. The system assumes that AI moderation pipelines are volatile and computationally expensive. Instead of blocking message delivery while waiting for NLP models to process, the system employs circuit breakers and timeouts. If the AI system fails, messages are still routed (fail-open) to maintain the chat experience, while fallback heuristics take over.

## Folder Structure
```text
toxichat/
├── backend/
│   ├── ai/                 # Core Machine Learning orchestration and models
│   ├── routers/            # FastAPI Endpoint groups (Auth, Chat)
│   ├── models/             # PyTorch/ONNX binary weights (cached)
│   ├── uploads/            # Temporary storage for avatars and unhashed media
│   ├── main.py             # FastAPI entry point & ASGI config
│   ├── database.py         # MongoDB connection & CRUD operations
│   ├── security.py         # Hashing, validation, sanitization
│   └── (service layers)    # incidents, audit, compliance, escalation, presence
│
└── frontend/
    ├── public/
    └── src/
        ├── components/
        │   ├── Admin/      # Evidence Viewers, Incident Management, Dashboards
        │   ├── Auth/       # Login/Registration
        │   ├── Chat/       # Message Bubbles, Inputs, Sidebar
        │   └── Common/     # Reusable UI (Buttons, Modals)
        ├── context/        # React Contexts (AuthContext, SocketContext)
        ├── services/       # api.js (Axios abstractions)
        └── App.js          # Main React router
```

## Design Decisions

1. **Python as the Sole Backend**: While Node.js is traditionally used for WebSocket applications, Python was selected because the entirety of the application's value proposition relies on PyTorch, HuggingFace, and ONNX. Utilizing FastAPI allows standard HTTP routing and WebSockets to exist in the exact same process boundary as the ML inference models, eliminating the network latency of microservice REST calls.
2. **MongoDB for Storage**: Toxicity analysis generates deeply nested, unpredictable JSON schemas (e.g., recursive arrays of `pii_entities`, lists of `vision_scores`, dynamically changing `explanation` graphs). A NoSQL document store handles this variability gracefully compared to rigid PostgreSQL tables.
3. **Redis Pub/Sub**: WebSocket connections are stateful and pinned to a specific worker process. To allow users on Worker A to chat with users on Worker B, Redis Pub/Sub acts as the central message bus.

## Limitations
1. **Thread Blocking**: The `ai.manager.py` orchestration runs asynchronously, but underlying libraries like `easyocr` and `faster-whisper` utilize heavy CPU bound loops that can occasionally block the Python event loop, increasing P99 latency for basic WebSocket pings.
2. **Memory Constraints**: Loading RoBERTa (Text), Whisper (Audio), and NudeNet (Vision) simultaneously into a single application context requires a minimum of 6GB-8GB RAM.
3. **In-Memory Fallback**: If MongoDB disconnects, the backend gracefully downgrades to a Python dictionary (`_use_memory`). This is excellent for keeping the system alive during DB outages but creates split-brain scenarios and guarantees data loss on application restart.

## Future Scalability Path
To scale ToxiChat to thousands of concurrent users:
1. **Decouple ML Workers**: Move `ai.manager.py` out of the FastAPI process. Standard chat messages should be placed on a Redis Queue or Kafka topic. A dedicated cluster of GPU-backed Python workers should consume these topics, process the moderation, and write results back to MongoDB/Redis.
2. **Database Sharding**: As chat volume grows, MongoDB should be sharded based on `conversation_id` or `receiver_id` to distribute write loads evenly.
