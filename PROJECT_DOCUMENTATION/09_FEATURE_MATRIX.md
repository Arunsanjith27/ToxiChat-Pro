# Feature Inventory & Status Matrix

This matrix provides a holistic view of every major feature within ToxiChat Pro, mapped to its underlying files, dependencies, and current operational status as of the latest audit.

| Feature Name | Purpose | Involved Files | Dependencies | Status | Notes |
|---|---|---|---|---|---|
| **User Authentication** | Registration, Login, and JWT generation with strict rate-limits and brute-force lockouts. | `auth.py`, `routers/auth_router.py`, `security.py`, `AuthContext.js` | bcrypt, python-jose, Redis (for lockouts) | 🟢 **Working** | Robust protection with 15-minute lockouts after 5 failed attempts. |
| **Real-Time Text Chat** | Core DM messaging with typing indicators, delivery receipts, and online presence. | `main.py` (WS router), `database.py`, `presence.py`, `ChatArea.jsx`, `MessageBubble.jsx` | WebSockets, Redis (Pub/Sub) | 🟢 **Working** | Fully operational. |
| **Group Chat** | Multi-user chat rooms. | `database.py`, `main.py` | WebSockets | 🟡 **Partial** | Backend fully supports group schemas and fan-out broadcasting, but the Frontend UI only partially exposes group creation. |
| **Pre-Send Interventions** | Intercepts toxic messages before sending, pushing a modal to the sender with a "Rewrite" suggestion. | `main.py`, `ai/manager.py`, `ai/rewrite_service.py`, `MessageBubble.jsx` | RoBERTa, HuggingFace Hub | 🟢 **Working** | Syntactic neutralization successfully preserves semantics while lowering toxicity. |
| **Image Evidence Inspector** | Allows admins to upload image attachments to scan for NSFW content and extract text via OCR. | `ai/image_moderation.py`, `ImageEvidenceViewer.jsx` | EasyOCR, NudeNet, ONNX | 🟢 **Working** | Repaired in recent patch (dependencies were missing, causing silent fails). |
| **Audio Evidence Inspector** | Allows admins to upload voice notes for deep speech-to-text transcription and audio corruption checks. | `ai/audio_moderation.py`, `AudioEvidenceViewer.jsx` | faster-whisper, pydub, ffmpeg | 🟢 **Working** | Repaired in recent patch. Accurately predicts language and returns timestamps. |
| **Report Generator** | Aggregates escalated messages, explanations, and risk matrices into a downloadable PDF/JSON Evidence Package. | `report_builder.py`, `compliance.py`, `generate_report.py`, `ComplianceDashboard.jsx` | ReportLab | 🟢 **Working** | Repaired in recent patch (fixed `unhashable list` bug in `copilot_context.py`). |
| **Conversation Summary** | Distills long chat threads into 1-paragraph summaries via NLP for quick moderator context. | `ai/conversation_intelligence.py`, `ConversationSummaryPanel.jsx` | HuggingFace (Summarization) | 🟢 **Working** | Highly effective for reducing moderator triage times. |
| **Moderator Copilot (Prediction)**| Analyzes conversational velocity to predict if a thread will escalate into a `CRITICAL` HR incident. | `ai/escalation_engine.py`, `ModeratorCopilotPanel.jsx`, `ConversationPredictionCard.jsx` | Custom heuristic algorithms | 🟢 **Working** | Accurately models timeline snapshots based on baseline analytics. |
| **Audit Trail** | Immutable, non-blocking ledger for critical actions (logins, logouts, mutes, admin actions). | `audit.py`, `AdminDashboard.jsx`, `AuditTrail/` | MongoDB | 🟢 **Working** | Fully visible in the Admin Dashboard. |
| **Automated User Penalties** | Issues strikes for toxic messages. Auto-mutes the user for 30 minutes on the 3rd strike, locking their WebSocket input. | `database.py` (`add_warning`), `main.py` | MongoDB | 🟢 **Working** | Triggers immediately over WS without requiring page refresh. |
| **Password Reset** | Generates secure URL-safe reset tokens with 1-hour TTL. | `auth_router.py`, `database.py` | MongoDB TTL Indexes | 🟡 **Partial** | Token generation and consumption works, but Email dispatch (SMTP) is mocked out in development. |
| **Semantic Search** | Allows users/admins to search chat history by semantic meaning (concept) rather than keyword matches. | `ai/embedding_service.py`, `database.py` | sentence-transformers | 🟢 **Working** | Embeddings are pre-generated on every message sent. |

## Legend
- 🟢 **Working**: Feature is fully implemented, tested, and operational in the runtime environment.
- 🟡 **Partial**: Feature works but relies on mock implementations, lacks full UI exposure, or is missing a peripheral integration (e.g., SMTP).
- 🔴 **Broken**: Feature causes 500s or crashes. (None currently known).
- ⚪ **Deprecated**: Feature retired.
