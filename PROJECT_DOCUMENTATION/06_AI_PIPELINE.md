# AI Pipeline Architecture

ToxiChat Pro utilizes a multi-modal, resilient orchestration engine for AI moderation. The core logic resides in `backend/ai/manager.py` which delegates to specialized micro-modules.

## The Core Text Moderation Pipeline
When a user sends a text message, it passes through an 8-step orchestrated pipeline before being saved and broadcasted. Each step runs via `resilience.execute_resilient` which wraps the execution in a circuit breaker with timeout and fallback logic.

1. **Emotion Detection** (`emotion_service.py`): Predicts the emotional undertone (e.g., Anger, Joy, Sadness, Neutral) to provide context for toxicity.
2. **Toxicity Detection** (`ml_service.py`): Uses context-aware analysis (e.g., a RoBERTa model) to assign a probability score and flag the message. Extracts toxic words.
3. **PII Detection** (`pii_service.py`): Scans for Personally Identifiable Information using regex/NLP models to flag entities like SSNs, Credit Cards, or Emails.
4. **Rewrite Engine** (`rewrite_service.py`): If toxicity is detected, this module attempts to syntactically neutralize the text while preserving its core semantic intent.
5. **Data Merge**: The orchestrator merges Emotion, Toxicity, and PII outputs into a unified dictionary.
6. **Risk Calculation** (`risk_engine.py`): Evaluates the combined data alongside conversation context to calculate an absolute Risk Score (0-100) and assign a Risk Level (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
7. **Explainability** (`explainability.py`): Generates a deterministic explanation (an array of reasons/alerts) justifying the risk score (e.g., "High toxicity combined with PII").
8. **Semantic Embedding** (`embedding_service.py`): Generates a vector embedding of the text for semantic search and clustering.

## Image Moderation Pipeline
The `analyze_image_orchestrator` handles image uploads.
1. **Validation & Hashing**: Computes SHA-256 for caching/tracking.
2. **Vision AI** (`image_moderation.py` / `NudeNet`): Detects explicit NSFW content or violence via ONNX runtime models.
3. **OCR Extraction** (`image_moderation.py` / `EasyOCR`): Extracts bounding boxes and text from the image.
4. **Text Routing**: If OCR extracts text, the text is routed back through the **Core Text Moderation Pipeline**.
5. **Score Aggregation**: Vision scores (NSFW) and Text scores are combined. If Vision NSFW > 0.6, the overall risk is hard-capped to `CRITICAL` (Score > 90).

## Audio Moderation Pipeline
The `analyze_audio_orchestrator` handles audio/voice notes.
1. **Validation & Hashing**: Computes SHA-256 and uses `pydub`/ffmpeg to verify file integrity and extract duration/channels.
2. **Speech-to-Text** (`audio_moderation.py` / `faster-whisper`): Transcribes the audio locally with timestamped segments and language prediction.
3. **Text Routing**: The final transcript is pushed through the **Core Text Moderation Pipeline**.
4. **Aggregation**: Audio metadata and text analysis are bundled for the frontend.

## Conversation Intelligence Pipeline
Instead of analyzing a single message, this pipeline analyzes the state of a thread.
1. **Conversation Analytics** (`conversation_analytics.py`): Computes statistical health (toxicity ratio, dominant emotion, PII instances, rewrite acceptance rate) across the last `N` messages.
2. **Conversation Summary** (`conversation_intelligence.py`): An LLM-based module that generates a human-readable summary of the thread, tailored for a specific persona (e.g., "moderator" vs "user").

## Prediction & Escalation Pipeline
The `escalation_engine.py` predicts whether a current conversation is trending toward a `CRITICAL` state.
1. It analyzes the risk velocity (how fast risk scores are increasing across sequential messages).
2. Uses cached Conversation Analytics to define the baseline state.
3. Outputs an Escalation Level, Trend (e.g., `STABLE`, `ESCALATING`), and generates a timeline for Moderator Copilot.

## Fault Tolerance & Resilience
Because ML inference is resource-heavy, all models are wrapped in `ai.resilience`. 
- **Timeouts**: If a model hangs (e.g., Whisper taking >30s), it is killed, and a fallback object is returned.
- **Fail-Open**: If Toxicity fails, the message is marked `clean` (or sent to human review) to prevent chat outages.
- **Circuit Breaking**: If an AI model fails sequentially, it is taken offline temporarily, and health endpoints report `DEGRADED`.
