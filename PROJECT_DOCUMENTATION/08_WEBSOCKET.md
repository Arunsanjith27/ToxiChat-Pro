# WebSocket Architecture

ToxiChat relies heavily on WebSockets for real-time bi-directional data flow. The implementation in `main.py` utilizes FastAPI's `WebSocket` endpoints and a custom `ConnectionManager`.

## Connection Lifecycle

1. **Connection & Authentication**:
   - Client connects to `ws://host:port/ws/{token}`.
   - Server verifies the JWT token via `verify_token(token)`. If invalid, the socket is immediately closed with `code=4001`.
2. **Presence & Handshake**:
   - On successful connection, the server records the connection in a centralized `presence.py` tracker (mapping username to active `set()` of socket connections).
   - If this is the *first* connection for the user, Redis is updated (`set_user_presence`), and a `presence_online` event is broadcasted.
   - The server immediately pushes a `users_list` packet down the pipe to bootstrap the client's sidebar.
3. **Disconnection**:
   - The connection is scrubbed from the `presence` tracker.
   - If the user has zero remaining open connections, they are marked offline in MongoDB (`update_last_seen`), Redis is updated, and a `presence_offline` broadcast occurs.

## Real-Time Messaging & Interventions

When a client sends a message (`msg_type == "message"`):

1. **Rate Limiting & Mute Checks**: 
   - A Redis rate-limit check (`auth_rate:{username}`) runs. If it trips, an error is sent.
   - MongoDB is checked for an active `mute_until` penalty. If muted, the message is dropped, and a `muted` packet is returned.
2. **Synchronous AI Processing**:
   - The raw text is passed to `ai_manager.analyze_message()`. This holds the websocket async event loop.
3. **The Pre-Send Warning Flow**:
   - If `tox["is_flagged"]` is `True` and the user did NOT pass `force_send: True`, the message is **blocked**.
   - The server sends back a `type: toxicity_pre_send` packet to the sender, containing the predicted score, offending words, and an AI-generated *safe rewrite* suggestion.
   - The sender's UI shifts into a modal state allowing them to `force_send` or accept the rewrite.
4. **Broadcasting**:
   - If the message passes or is force-sent, it's saved to MongoDB.
   - The server routes the message to the intended recipient (DM) or loop (Group Chat).
   - If the message was force-sent and flagged, the recipient receives a `toxicity_warning` packet ("Incoming message may contain harmful content") right before the actual message packet arrives.
5. **Punitive Actions**:
   - If flagged, the server issues an internal warning (`add_warning()`). It sends a `toxicity_alert` packet. If this was the 3rd warning, the user is instantly muted, and a `muted` packet is sent to lock their UI.

## Auxiliary Events

- **Typing Indicators**: `type: typing`. Routed directly to the recipient to display an animation.
- **Seen/Delivered Receipts**:
   - Handled via `type: mark_seen`. 
   - If the recipient is currently online (checked via `presence.is_user_online`), the server immediately flags the message as "delivered" in MongoDB and reflects this via a `status_update` packet to the sender.
- **Reactions**: 
   - Handled via `type: reaction`. Updates MongoDB and broadcasts to the recipient.
- **Administrative Telemetry**:
   - If the message breached critical thresholds, the `escalation` matrix triggers logic (e.g. `incidents.create_incident()`) asynchronously in the background.
