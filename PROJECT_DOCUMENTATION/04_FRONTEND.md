# Frontend Architecture

ToxiChat Pro's frontend is a Single Page Application (SPA) built with **React**. It heavily utilizes modern hooks, context providers, and TailwindCSS to deliver a highly interactive, real-time dashboard and chat interface.

## Core Setup
- **Framework**: Create React App (CRA) / Webpack.
- **Styling**: TailwindCSS provides utility classes for rapid UI construction, allowing components to remain self-contained without sprawling CSS stylesheets.
- **Icons**: `lucide-react` provides standardized, lightweight SVG icons.
- **Routing**: Client-side routing managed by `react-router-dom`, protecting admin and user routes based on the active JWT session.

## State Management
ToxiChat eschews heavy state libraries like Redux in favor of native React Contexts to manage global state:
1. **AuthContext**: Manages the user's JWT, profile data (avatar, role, reputation), and authentication state. It intercepts HTTP 401s to force logouts.
2. **SocketContext**: Manages the singleton WebSocket connection. It handles connection retries, authentication handshakes, and broadcasts incoming events (messages, typing indicators) to any subscribed component.

## Component Hierarchy & Modularity

The frontend is divided into domain-specific subdirectories under `src/components/`:

### 1. Chat Domain
- **`MessageBubble.jsx`**: A highly complex component responsible for rendering text, handling AI risk colors, rendering "Rewrite" suggestions, and parsing inline Markdown.
- **`ChatArea.jsx`**: The main conversational viewport. Connects to `SocketContext` to render real-time messages.
- **`ChatInput.jsx`**: Handles typing events, emitting them over WebSockets to inform the recipient.

### 2. Admin & Compliance Domain
The Admin dashboard is a sophisticated suite of diagnostic and compliance tools:
- **`AdminDashboard.jsx`**: The central hub routing to different diagnostic panes.
- **`IncidentManagement/`**: A suite of components (`IncidentDashboard`, `IncidentDetails`, `IncidentTimeline`) that visualize the lifecycle of an escalated chat, complete with historical snapshots and assignment tracking.
- **`ComplianceReports/`**: Views the output of `report_builder.py`, rendering formal evidence packages for HR or legal review.
- **`Raw AI Telemetry`**: Displays raw JSON dumps and latency metrics from the backend ML orchestrators.

### 3. Moderation Viewers
These components interact with the multimodal ML pipelines:
- **`ImageEvidenceViewer.jsx`**: Uploads images to the `/api/image/analyze` endpoint. Renders OCR extraction bounding boxes, text safety stats, and NSFW probability scores. Allows downloading a text-based "evidence package".
- **`AudioEvidenceViewer.jsx`**: Uploads audio to `/api/audio/analyze`. Provides an audio playback wrapper and renders the `faster-whisper` generated transcript alongside toxicity scores.
- **`ModeratorCopilotPanel.jsx`**: Triggers the `/api/conversation/prediction` endpoint, rendering an interactive timeline predicting whether the active chat thread is trending toward a critical escalation.

## API & Network Layer
- **`services/api.js`**: Contains abstracted Axios calls. It centralizes error handling, automatically attaching the `Authorization: Bearer <token>` header to all requests, and mapping backend JSON endpoints to frontend JS promises.

## Real-time Execution Flow
1. User types in `ChatInput`. The component throttles and emits `{"type": "typing"}` over the WebSocket.
2. User submits the message. It is appended optimistically to the local state as `status: pending`.
3. The message is sent to the backend. The backend processes it via AI pipelines.
4. The backend broadcasts the validated, moderated message back via WebSocket.
5. The `SocketContext` receives the message, updates the local state, and `MessageBubble` re-renders, displaying any AI rewrites or warning colors if the message was flagged.
