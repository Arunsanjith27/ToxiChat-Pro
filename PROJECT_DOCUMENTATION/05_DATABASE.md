# Database Architecture & Schemas

ToxiChat Pro utilizes **MongoDB** as its primary data store, accessed asynchronously via the `motor` (MotorAsyncIO) driver in `backend/database.py`.

## Connection & Resiliency
- **Connection Logic**: The system attempts to connect to `MONGO_URL` up to 3 times (`MAX_RETRIES`).
- **TLS Support**: It natively checks if TLS is required via `mongodb+srv://` or `tls=true` and injects `certifi` CA files.
- **In-Memory Fallback**: If MongoDB is completely unreachable, the system gracefully degrades into `_use_memory = True` mode. It provisions an ephemeral dictionary structure (`{"users": [], "messages": [], "groups": [], "reset_tokens": []}`) to prevent the application from crashing. *Warning: Data is lost on server restart in this mode.*

## Collections and Indexes

### 1. `users` Collection
Stores user profiles, roles, reputation, and muting history.
- **Index**: `username` (Unique)
- **Schema**:
  - `username` (str): Unique identifier
  - `password` (str): Bcrypt hashed password
  - `display_name` (str): UI friendly name
  - `role` (str): `user` or `admin`
  - `is_muted` (bool): Active mute status
  - `mute_until` (datetime): Expiration for the mute
  - `mute_history` (list[dict]): Audit trail of past mutes
  - `reputation_score` (int): 0-100 score updated on every message
  - `reputation_tier` (str): E.g., `excellent`, `poor`
  - `total_messages`, `toxic_messages` (int): Analytics counters

### 2. `messages` Collection
Stores all chat messages including deep AI telemetry.
- **Indexes**: 
  - `timestamp` (Ascending)
  - `is_flagged` (For rapid admin dashboard queries)
  - `sender, receiver` (Compound for DM lookups)
  - `sender, receiver, timestamp` (Compound for rapid chronological DM loading)
- **Schema**:
  - `id` (str): `msg_{timestamp}`
  - `sender` (str): Username of the sender
  - `receiver` (str): Username of the receiver (or group name)
  - `is_group` (bool): True if group chat
  - `text` (str): Original text
  - `timestamp` (isoformat): Insertion time
  - `is_flagged` (bool): High-level toxicity flag
  - `toxic_words` (list[str]): Extracted by AI
  - `toxicity_score` (float), `risk_score` (int), `risk_level` (str)
  - `emotion` (str), `emotion_confidence` (float)
  - `contains_pii` (bool), `pii_entities` (list[str])
  - `rewrite` (str): The AI-generated safe version of the message
  - `explanation` (dict): Reasons for risk scores
  - `reactions` (list[dict]): `{"username": str, "emoji": str, "timestamp": str}`

### 3. `groups` Collection
Stores group chat metadata.
- **Schema**:
  - `name` (str): Group identifier
  - `members` (list[str]): Array of usernames
  - `creator` (str): Username of the creator
  - `created_at` (isoformat)

### 4. `reset_tokens` Collection
Handles password reset functionality.
- **Index**: `token` (Unique), `expires_at` (TTL Index - `expireAfterSeconds=0`)
- **Schema**:
  - `token` (str): 32-byte URL safe token
  - `username` (str): Target user
  - `expires_at` (datetime): TTL deletion target

## Advanced Querying & Aggregation

### Conversation Lookup (Robust Fallback)
The `get_messages_for_conversation` function implements a robust MongoDB `$expr` query. If exact participants aren't provided but a compound `conversation_id` (e.g., `userA_userB`) is sent, the database performs a dynamic string concatenation to resolve the chat history:
```json
{
  "$expr": {
    "$or": [
      {"$eq": [{"$concat": ["$sender", "_", "$receiver"]}, "conversation_id"]},
      {"$eq": [{"$concat": ["$receiver", "_", "$sender"]}, "conversation_id"]}
    ]
  }
}
```

### Dashboard Statistics
The `get_dashboard_stats` executes a heavy aggregation across the entire messages collection (limited to 10,000 for performance):
- It aggregates hourly/daily message volume and toxicity rates.
- It calculates `rewrite_success_rate`.
- It identifies `critical_conversations` by passing recent message windows directly into the AI `predict_escalation` module on-the-fly.
- Uses `$group` and `$sort` aggregations in `get_active_conversations` to pull a unified list of the most recent DMs and Groups.

## Analytics Update Hooks
When `save_message` is triggered, an asynchronous hook `_increment_user_message_stats` fires. This invokes the `escalation.compute_reputation` algorithm, dynamically adjusting the user's overall `reputation_score` and `reputation_tier` based on their total volume vs. toxic volume, injecting game-theory-like behavioral economics into the chat platform.
