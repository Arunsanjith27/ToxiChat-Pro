# Technical Glossary

This glossary defines domain-specific terminology, acronyms, and concepts utilized throughout the ToxiChat platform and its documentation.

## A
- **ASGI (Asynchronous Server Gateway Interface)**: The spiritual successor to WSGI. It provides a standard interface between async-capable Python web servers (like Uvicorn) and applications (like FastAPI), allowing for non-blocking WebSockets.
- **Audit Trail**: An immutable, chronological ledger stored in MongoDB recording every significant administrative or security event (e.g., logins, mutes, incident creations).

## C
- **Copilot (Moderator Copilot)**: A suite of AI-driven tools within the admin dashboard that assists human moderators by summarizing long conversation threads and predicting future escalations.

## E
- **EasyOCR**: A PyTorch-based Optical Character Recognition library used in the Image Evidence Inspector to extract text embedded within images.
- **Escalation Velocity**: A metric calculated by the AI orchestrator measuring how rapidly the risk score of a conversation is increasing over a sequence of messages.

## F
- **Fail-Open**: A resiliency design pattern. If a non-critical system (like the AI toxicity pipeline) fails, the core system (message routing) continues to operate, rather than crashing or blocking the user experience.

## I
- **Incident**: A point-in-time snapshot of a conversation that has breached a `CRITICAL` risk threshold. Incidents are tracked, assigned to moderators, and used to generate formal compliance reports.
- **In-Memory Fallback**: A system state triggered when the MongoDB connection fails. ToxiChat downgrades to using volatile Python dictionaries to prevent application crashes, at the cost of data persistence.

## M
- **Modular Monolith**: A software architecture style where all components (APIs, WebSockets, Machine Learning) reside in a single deployable codebase (a monolith) but are strictly separated by domain boundaries (modular) to allow for easier future extraction into microservices.

## N
- **NudeNet**: A neural network optimized for detecting Not-Safe-For-Work (NSFW) imagery and violence. ToxiChat executes this via the ONNX runtime for CPU/GPU portability.

## O
- **OCR (Optical Character Recognition)**: The mechanical or electronic conversion of images of typed, handwritten or printed text into machine-encoded text.
- **ONNX (Open Neural Network Exchange)**: An open format built to represent machine learning models. It allows models trained in PyTorch to run highly efficiently in production environments without the full PyTorch dependency overhead.

## P
- **PII (Personally Identifiable Information)**: Information that can be used to identify a specific individual (e.g., Social Security Numbers, phone numbers, credit cards).
- **Pub/Sub (Publish/Subscribe)**: A messaging pattern where senders (publishers) categorize messages into classes (topics) without knowledge of the receivers (subscribers). ToxiChat uses Redis Pub/Sub to distribute WebSocket messages across multiple server instances.

## R
- **RBAC (Role-Based Access Control)**: A method of restricting network access based on the roles of individual users within an enterprise (`user` vs `admin`).
- **Reputation Score**: A dynamically calculated integer (0-100) assigned to every user, functioning as a behavioral credit score. It drops when sending toxic messages and slowly recovers over time as safe messages are sent.
- **RoBERTa (Robustly Optimized BERT Pretraining Approach)**: A state-of-the-art natural language processing model developed by Facebook AI. ToxiChat fine-tunes versions of this architecture to detect toxicity and emotion.

## T
- **Telemetry**: In the context of ToxiChat, this refers to the raw JSON metadata produced by the AI pipelines (e.g., probability tensors, extracted entities, risk distributions) attached to every message.

## W
- **Whisper (faster-whisper)**: An automatic speech recognition (ASR) system trained by OpenAI. ToxiChat uses a highly optimized CTranslate2 implementation (`faster-whisper`) to transcribe voice notes in the Audio Evidence Inspector.
