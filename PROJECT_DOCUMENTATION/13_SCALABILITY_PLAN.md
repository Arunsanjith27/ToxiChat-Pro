# Scalability Plan & Architecture Evolution

ToxiChat Pro currently operates as a **Modular Monolith**. While this allows for rapid development and avoids complex distributed tracing, the inclusion of heavy machine learning inference in the same process space as the WebSocket handlers creates an inherent bottleneck. 

To support enterprise scale (10,000+ concurrent users), the architecture must evolve.

## Phase 1: Decoupling ML Inference (The Worker Queue)
Currently, `ai.manager.analyze_message` holds the FastAPI async event loop waiting for PyTorch/HuggingFace to return.
- **Action**: Extract `ai/manager.py` into a standalone Celery or RabbitMQ worker service.
- **Execution**: 
  1. FastAPI receives the WebSocket message.
  2. FastAPI pushes the message payload to a Redis Queue and immediately yields.
  3. A pool of GPU-accelerated Python worker nodes consume the queue, execute the Toxicity/Emotion models, and write the result directly to MongoDB.
  4. The worker publishes the result back via Redis Pub/Sub to the specific FastAPI node holding the user's WebSocket connection.
- **Benefit**: WebSocket latency drops to sub-10ms. AI node scaling becomes independent of connection node scaling.

## Phase 2: Database Sharding
MongoDB currently stores all messages in a single collection. As volume grows, the index size will exceed RAM.
- **Action**: Shard the `messages` collection.
- **Execution**: Use `conversation_id` (a hash of `sender_receiver` or `group_name`) as the Shard Key. This ensures that all messages for a specific chat thread reside on the same physical MongoDB replica set, maintaining chronological query speed.
- **Benefit**: Infinite horizontal scaling for message storage.

## Phase 3: Edge Routing & Pub/Sub Evolution
Redis Pub/Sub is currently used to fan out WebSocket broadcasts across multiple Uvicorn instances. At massive scale, Redis Pub/Sub CPU utilization can spike.
- **Action**: Migrate the message bus.
- **Execution**: Replace Redis Pub/Sub with Apache Kafka or Google Cloud Pub/Sub for guaranteed ordering, persistent event sourcing, and consumer group load balancing.
- **Benefit**: Ensures no messages are lost during server restarts and handles millions of events per second.

## Phase 4: Cold Storage & Analytics Warehousing
ToxiChat retains telemetry (toxicity vectors, explanations) forever, which is expensive.
- **Action**: Implement a data lifecycle policy.
- **Execution**: 
  1. Messages older than 90 days are extracted from MongoDB.
  2. They are transformed into Parquet files and pushed to Amazon S3 / Google Cloud Storage.
  3. A data warehouse (Snowflake / BigQuery) is layered over the cold storage to allow compliance officers to run complex multi-year audit queries.
- **Benefit**: Reduces hot storage costs by 90% while maintaining compliance.
