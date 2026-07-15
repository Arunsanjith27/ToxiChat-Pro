# User Roles & Access Control

ToxiChat utilizes a strict, binary Role-Based Access Control (RBAC) mechanism consisting of `user` and `admin` roles, though the `admin` role is functionally utilized across several real-world personas.

## The Standard `user`
This is the default role assigned to any new registration via `/api/register`.

**Capabilities:**
- Authenticate and maintain a WebSocket connection.
- Send and receive Direct Messages (DMs) and participate in Group Chats.
- Trigger the Pre-Send AI Warning modal when their own inputs are flagged.
- View their own profile statistics (`warnings_count`, `reputation_tier`).

**Restrictions:**
- Cannot view global dashboards or analytics.
- Cannot query the `users` collection for anyone other than themselves.
- Cannot interact with the incident management or report generation engines.

## The Privileged `admin`
A user is granted admin privileges dynamically if their username exists in the `.env` variable `ADMIN_USERNAMES` at boot time, or if another admin manually updates their MongoDB document to `{ "role": "admin" }` via the `/api/admin/action` endpoint.

### Real-World Persona Mapping

Within the system, all of the following personas share the technical `admin` token, but they utilize different segments of the frontend dashboard:

#### 1. Compliance Officer / HR
- **Primary Interface**: Incident Management & Compliance Reports.
- **Workflow**: Receives alerts that a conversation breached a `CRITICAL` risk threshold. They use the `report_builder.py` endpoints to download cryptographically hashed PDF evidence packages for legal/HR offboarding processes.

#### 2. Live Moderator
- **Primary Interface**: Moderator Copilot Panel & Active Dashboards.
- **Workflow**: Monitors the `ConversationPredictionCard` to see if active chat threads are accelerating toward toxicity. They rely on the AI's thread summarizations to quickly triage an escalating situation without reading 100+ raw messages. They manually invoke the `mute` action against hostile actors.

#### 3. System Administrator
- **Primary Interface**: Raw AI Telemetry & Audit Trail.
- **Workflow**: Monitors the inference latency of the PyTorch/ONNX models. Inspects the global Audit Trail for suspicious login activity (e.g., brute force lockouts) or unexpected privilege escalations.

## Privileged Endpoints (`require_admin`)
Any endpoint decorated with `Depends(require_admin)` will return a `403 Forbidden` if accessed by a standard user.
- `/api/admin/*` (All dashboard and manual penalty actions)
- `/api/reports/generate`
- `/api/audit`
- `/api/image/analyze` & `/api/audio/analyze` (Restricted to prevent users from consuming massive GPU resources via media spam).
