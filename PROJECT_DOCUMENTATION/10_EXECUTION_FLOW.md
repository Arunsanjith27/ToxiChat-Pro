# Critical Execution Flows

Understanding the sequence of events is critical for debugging ToxiChat. Below are the execution traces for the most complex system pathways.

## Flow 1: Pre-Send Toxic Message Interception

This flow describes what happens when a user attempts to send a highly toxic message, and the AI steps in *before* the message reaches the database.

1. **Client (React)**: User clicks "Send" in `ChatInput.jsx`.
2. **Client (React)**: Component emits a WebSocket packet: `{"type": "message", "text": "I hate you!", "receiver": "bob"}`.
3. **Backend (`main.py`)**: `websocket_endpoint` receives the JSON.
4. **Backend (Redis)**: Rate limit counter is incremented.
5. **Backend (MongoDB)**: `db.check_mute(username)` verifies the user isn't serving a penalty.
6. **Backend (`ai.manager.py`)**: The text is passed into the `analyze_message()` orchestrator.
7. **ML Models (HuggingFace)**: 
   - `emotion_service` detects Anger.
   - `ml_service` flags the text as Toxic (Score: 0.98).
8. **Rewrite Engine (`ai.rewrite_service.py`)**: Because `is_flagged == True`, the text is fed into the rewrite algorithm, returning: "I strongly disagree with you."
9. **Risk Engine (`ai.risk_engine.py`)**: Combines Emotion and Toxicity to evaluate the Risk Level (e.g., `MEDIUM`).
10. **Backend (`main.py`)**: The orchestration returns. `tox["is_flagged"]` is `True`.
11. **Escalation Engine (`escalation.py`)**: Calculates predictive escalation based on the last 10 messages between these users.
12. **Backend (`main.py`)**: The WebSocket intercepts the routing. Instead of broadcasting to Bob, it returns a `type: toxicity_pre_send` packet *back to the sender*.
13. **Client (React)**: `MessageBubble.jsx` intercepts the `toxicity_pre_send` packet, morphing the input UI into an orange "Warning Modal" displaying the AI's rewrite suggestion.
14. **Client (React)**: The user clicks "Accept Rewrite" or "Send Anyway (Force)". 
15. **Backend (`main.py`)**: If "Force" is clicked, the system logs a strike against the user (`add_warning`) and finally routes the message to Bob.

## Flow 2: Multi-Modal Incident Evidence Reporting

This flow describes how an administrator generates a compliance report after an image or audio file is flagged.

1. **Client (AdminDashboard)**: Admin opens the `ImageEvidenceViewer`.
2. **Client (React)**: Admin selects an image and submits it. `api.js` makes a `POST /api/image/analyze` request with `multipart/form-data`.
3. **Backend (`main.py`)**: FastAPI endpoint receives the file bytes.
4. **AI Orchestrator (`ai.manager.py`)**: `analyze_image_orchestrator` is invoked.
5. **Vision AI (`image_moderation.py`)**: NudeNet scans the image array, returning an NSFW probability (e.g., 0.85).
6. **OCR AI (`image_moderation.py`)**: EasyOCR extracts bounding boxes. It finds the text: "Send the secret files now."
7. **Text Orchestrator (`ai.manager.py`)**: The extracted text is routed into the standard text pipeline, where it's checked for toxicity, PII, and risk.
8. **Backend (`main.py`)**: The merged JSON (Image Hash, NSFW Score, OCR Data, Text Toxicity) is returned to the React client.
9. **Client (React)**: `ImageEvidenceViewer` visualizes the OCR bounding boxes via an HTML5 Canvas overlay.
10. **Client (React)**: The Admin clicks "Generate Incident Report". 
11. **Backend (`report_builder.py`)**: `POST /api/reports/generate` triggers the builder. The builder pulls the cached message/image telemetry and creates a structured JSON payload.
12. **Backend (`test_pdf.py` logic)**: The user downloads the report. The backend utilizes `reportlab` to compile the JSON telemetry, timelines, and explanations into a formatted, cryptographically hashed PDF.
13. **Client (React)**: The browser triggers a file download for `evidence_report_123.pdf`.
