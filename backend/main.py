import os
import json
from datetime import datetime
from typing import Dict, Optional, List, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import routers.auth_router
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv(override=True)

import models
from models import (
    UserRegister, UserLogin, TokenOut, UserOut,
    ToxicityRequest, ToxicityResult, DashboardStats, GroupCreate, RewriteRequest,
    ForgotPasswordRequest, ResetPasswordRequest, ProfileUpdate,
    EscalationRequest, EscalationResult, AdminAction, ConversationHealth,
    ConversationAnalyticsResult
)
import database as db
import presence
import ai.manager as ai_manager
import incidents
import audit
import compliance
import redis_service
from security import hash_password, verify_password, migrate_password, sanitize_input, validate_file
from auth import (
    create_token, verify_token, get_current_user, require_admin, is_admin_user,
)

RATE_LIMIT_MSG = int(os.getenv("RATE_LIMIT_MSG", "30"))
CORS_ORIGINS_ENV = os.getenv("CORS_ORIGINS", "*").split(",")
CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS_ENV if origin.strip()]

AVATAR_DIR = os.path.join(os.path.dirname(__file__), "uploads", "avatars")
os.makedirs(AVATAR_DIR, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.get_db()
    await redis_service.init_redis()

    # Register all AI modules with the resilience health tracker
    import ai.resilience as resilience
    for module_name in [
        "Emotion", "Toxicity", "PII", "Rewrite", "Risk", "Explainability",
        "Embedding", "Conversation Analytics", "Conversation Intelligence",
        "Image Moderation", "Audio Moderation", "Prediction",
        "Copilot Context", "Moderator Copilot",
    ]:
        resilience.register_module(module_name)

    print("[OK] ToxiChat Pro API ready")
    yield

app = FastAPI(title="ToxiChat Pro API", version="3.0.0", lifespan=lifespan)

allow_origins = []
allow_origin_regex = None

if CORS_ORIGINS == ["*"]:
    allow_origin_regex = ".*"
else:
    allow_origins = CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

app.add_middleware(SecurityHeadersMiddleware)
app.include_router(routers.auth_router.router)

app.mount("/uploads", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "uploads")), name="uploads")


@app.get("/api/me", response_model=UserOut)
async def get_me(username: str = Depends(get_current_user)):
    user = await db.get_user(username)
    if not user:
        raise HTTPException(404, "User not found")
    return UserOut(
        username=user["username"],
        display_name=user.get("display_name", username),
        created_at=user.get("created_at", ""),
        is_online=user.get("is_online", False),
        warnings_count=user.get("warnings_count", 0),
        is_muted=user.get("is_muted", False),
        avatar_url=user.get("avatar_url"),
        bio=user.get("bio", ""),
        reputation_score=user.get("reputation_score", 100),
        reputation_tier=user.get("reputation_tier", "excellent"),
        role=user.get("role", "user"),
    )


@app.put("/api/profile", response_model=UserOut)
async def update_profile(data: ProfileUpdate, username: str = Depends(get_current_user)):
    updated = await db.update_user_profile(username, data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(404, "User not found")
    return UserOut(
        username=updated["username"],
        display_name=updated.get("display_name", username),
        created_at=updated.get("created_at", ""),
        is_online=updated.get("is_online", False),
        warnings_count=updated.get("warnings_count", 0),
        is_muted=updated.get("is_muted", False),
        avatar_url=updated.get("avatar_url"),
        bio=updated.get("bio", ""),
        reputation_score=updated.get("reputation_score", 100),
        reputation_tier=updated.get("reputation_tier", "excellent"),
        role=updated.get("role", "user"),
    )


@app.post("/api/profile/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    username: str = Depends(get_current_user),
):
    content = await file.read()
    if not validate_file(file.content_type or "", len(content)):
        raise HTTPException(400, "Invalid file type or size (max 10MB, images only)")
    ext = (file.filename or "avatar.png").rsplit(".", 1)[-1].lower()
    if ext not in {"png", "jpg", "jpeg", "gif", "webp"}:
        ext = "png"
    filename = f"{username}.{ext}"
    filepath = os.path.join(AVATAR_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(content)
    avatar_url = f"/uploads/avatars/{filename}"
    await db.update_user_profile(username, {"avatar_url": avatar_url})
    return {"avatar_url": avatar_url}


@app.get("/api/users")
async def list_users(username: str = Depends(get_current_user)):
    return await db.get_all_users()


@app.get("/api/ai/health")
async def get_ai_health(username: str = Depends(get_current_user)):
    import ai.resilience as r
    return r.get_ai_health()

@app.post("/api/predict", response_model=ToxicityResult)
async def predict(data: ToxicityRequest, username: str = Depends(get_current_user)):
    result = await ai_manager.analyze_message(data.text)
    emb = result.get("embedding", [])
    with open("debug_log.txt", "a") as f:
        f.write(f"predict called! emb length: {len(emb)}\n")
        if not emb:
            import ai.resilience as r
            f.write(f"Health: {r.get_ai_health()}\n")
    return ToxicityResult(text=data.text, **result)


@app.post("/api/predict/escalation", response_model=EscalationResult)
async def predict_escalation(data: EscalationRequest, username: str = Depends(get_current_user)):
    recent = await db.get_conversation_messages(username, data.partner, limit=15)
    context = [m.get("text", "") for m in recent]
    result = await ai_manager.analyze_message(data.text, context=recent)
    from escalation import predict_escalation as calc_escalation
    esc = calc_escalation(recent, result["score"], result["is_flagged"])
    return EscalationResult(
        text=data.text,
        score=result["score"],
        label=result["label"],
        is_flagged=result["is_flagged"],
        toxic_words=result.get("toxic_words", []),
        emotion=result.get("emotion", "neutral"),
        emotion_confidence=result.get("emotion_confidence", 0.0),
        contains_pii=result.get("contains_pii", False),
        pii_entities=result.get("pii_entities", []),
        rewrite=result.get("rewrite"),
        escalation=esc,
        conversation_health=esc["conversation_health"],
    )


@app.post("/api/rewrite")
async def rewrite(data: RewriteRequest, username: str = Depends(get_current_user)):
    import ai.manager as manager
    import ai.rewrite_service as rewrite_service
    # Need to run toxicity analysis to validate rewrite
    analysis = await manager.analyze_message(data.text)
    result = rewrite_service.rewrite_message(data.text, analysis)
    
    # Return original text if rewrite failed to preserve meaning or reduce toxicity
    rewritten_text = result.get("rewritten_text") or data.text
    return {"original": data.text, "rewritten": rewritten_text}


@app.get("/api/search")
async def search_messages(q: str = "", limit: int = 50, username: str = Depends(get_current_user)):
    with open("main_search_debug.log", "a") as f:
        f.write(f"Hit /api/search with q={q}, username={username}\n")
    return await db.search_messages(q, username, limit)

class SummaryRequest(BaseModel):
    conversation_id: str
    summary_type: str = "moderator"
    participants: Optional[List[str]] = None
    is_group: Optional[bool] = None

@app.post("/api/conversation/summary")
async def generate_summary(req: SummaryRequest, username: str = Depends(get_current_user)):
    # Validate access (simplified for now, assumes username is authorized)
    summary_res = await ai_manager.summarize_conversation(
        req.conversation_id, 
        req.summary_type,
        participants=req.participants,
        is_group=req.is_group
    )
    return summary_res

@app.post("/api/image/analyze", response_model=models.ImageAnalysisResponse)
async def analyze_image_upload(file: UploadFile = File(...), username: str = Depends(get_current_user)):
    try:
        file_bytes = await file.read()
        res = await ai_manager.analyze_image_orchestrator(file_bytes, file.content_type)
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/audio/analyze", response_model=models.AudioAnalysisResponse)
async def analyze_audio_upload(file: UploadFile = File(...), username: str = Depends(get_current_user)):
    try:
        file_bytes = await file.read()
        res = await ai_manager.analyze_audio_orchestrator(file_bytes, file.content_type)
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversation/analytics/{conversation_id}")
async def get_conversation_analytics_api(
    conversation_id: str,
    user1: Optional[str] = None,
    user2: Optional[str] = None,
    is_group: Optional[bool] = None,
    username: str = Depends(get_current_user)
):
    try:
        participants = None
        if user1 and user2:
            participants = [user1, user2]
        elif user1:
            participants = [user1]
        res = await ai_manager.analyze_conversation_orchestrator(
            conversation_id,
            participants=participants,
            is_group=is_group
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversation/prediction/{conversation_id}", response_model=models.EscalationPredictionResponse)
async def get_conversation_prediction_api(
    conversation_id: str,
    user1: Optional[str] = None,
    user2: Optional[str] = None,
    is_group: Optional[bool] = None,
    username: str = Depends(get_current_user)
):
    try:
        participants = None
        if user1 and user2:
            participants = [user1, user2]
        elif user1:
            participants = [user1]
        res = await ai_manager.predict_conversation_escalation(
            conversation_id,
            participants=participants,
            is_group=is_group
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/admin/copilot", response_model=models.CopilotResponse)
async def ask_moderator_copilot_api(req: models.CopilotRequest, username: str = Depends(get_current_user)):
    try:
        res = await ai_manager.ask_moderator_copilot(
            req.conversation_id,
            req.question,
            participants=req.participants,
            is_group=req.is_group
        )
        
        # Async Audit Log
        await audit.log_event(
            actor_username=username,
            action="COPILOT_USED",
            resource_type="CONVERSATION",
            resource_id=req.conversation_id,
            conversation_id=req.conversation_id,
            description=f"Moderator asked Copilot: {req.question}"
        )
        
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# INCIDENT MANAGEMENT API
# ==========================================

@app.post("/api/incidents")
async def create_incident_api(req: models.CreateIncidentRequest, username: str = Depends(get_current_user)):
    try:
        return await incidents.create_incident(
            req.conversation_id, 
            req.priority, 
            created_by=username,
            participants=req.participants,
            is_group=req.is_group
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        raise HTTPException(status_code=500, detail=tb)

@app.get("/api/incidents")
async def list_incidents_api(status: Optional[str] = None, priority: Optional[str] = None, username: str = Depends(get_current_user)):
    try:
        return await incidents.list_incidents(status, priority)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/incidents/{incident_id}")
async def get_incident_api(incident_id: str, username: str = Depends(get_current_user)):
    try:
        return await incidents.get_incident(incident_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/incidents/{incident_id}")
async def update_incident_status_api(incident_id: str, req: models.UpdateIncidentStatusRequest, username: str = Depends(get_current_user)):
    try:
        return await incidents.update_status(incident_id, req.status)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/incidents/{incident_id}/assign")
async def assign_incident_api(incident_id: str, req: models.AssignIncidentRequest, username: str = Depends(get_current_user)):
    try:
        return await incidents.assign_incident(incident_id, req.assignee, assigned_by=username)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/incidents/{incident_id}/resolve")
async def resolve_incident_api(incident_id: str, username: str = Depends(get_current_user)):
    try:
        return await incidents.resolve_incident(incident_id, resolved_by=username)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/incidents/{incident_id}/archive")
async def archive_incident_api(incident_id: str, username: str = Depends(get_current_user)):
    try:
        return await incidents.archive_incident(incident_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/incidents/{incident_id}/notes")
async def add_incident_note_api(incident_id: str, req: models.AddIncidentNoteRequest, username: str = Depends(get_current_user)):
    try:
        return await incidents.add_note(incident_id, req.content, author=username, internal_only=req.internal_only)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/incidents/{incident_id}/notes")
async def get_incident_notes_api(incident_id: str, username: str = Depends(get_current_user)):
    try:
        return await incidents.get_incident_notes(incident_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# AUDIT TRAIL API
# ==========================================

@app.get("/api/audit")
async def get_audit_logs_api(action: Optional[str] = None, actor: Optional[str] = None, username: str = Depends(get_current_user)):
    if not is_admin_user(username):
        raise HTTPException(status_code=403, detail="Not authorized to view global audit logs.")
    return await audit.get_audit_logs(limit=100, action=action, actor=actor)

@app.get("/api/audit/incident/{incident_id}")
async def get_incident_audit_api(incident_id: str, username: str = Depends(get_current_user)):
    try:
        return await audit.get_incident_history(incident_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/audit/user/{target_username}")
async def get_user_audit_api(target_username: str, username: str = Depends(get_current_user)):
    try:
        if not is_admin_user(username):
            raise HTTPException(status_code=403, detail="Not authorized.")
        return await audit.get_user_activity(target_username)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# COMPLIANCE REPORT API
# ==========================================

@app.post("/api/reports/generate")
async def generate_report_api(req: models.GenerateReportRequest, username: str = Depends(get_current_user)):
    if not is_admin_user(username):
        raise HTTPException(status_code=403, detail="Not authorized.")
    report = await compliance.generate_report(req.incident_id, generated_by=username)
    return report

@app.get("/api/reports/{report_id}")
async def get_report_api(report_id: str, username: str = Depends(get_current_user)):
    try:
        return await compliance.get_report(report_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.responses import Response

@app.get("/api/reports/download/{report_id}")
async def download_report_api(report_id: str, format: str = "pdf", username: str = Depends(get_current_user)):
    try:
        report = await compliance.get_report(report_id)
        if format == "pdf":
            pdf_bytes = compliance.export_pdf(report["report_object"])
            return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=report_{report_id}.pdf"})
        elif format == "html":
            html_str = compliance.export_html(report["report_object"])
            return Response(content=html_str, media_type="text/html")
        elif format == "markdown" or format == "md":
            md_str = compliance.export_markdown(report["report_object"])
            return Response(content=md_str, media_type="text/markdown")
        else:
            json_str = compliance.export_json(report["report_object"])
            return Response(content=json_str, media_type="application/json")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/messages/{user1}/{user2}")
async def get_messages(user1: str, user2: str, username: str = Depends(get_current_user)):
    if username not in (user1, user2):
        raise HTTPException(403, "Access denied to this conversation")
    return await db.get_messages(user1, user2)


@app.get("/api/conversation/health/{partner}", response_model=ConversationHealth)
async def conversation_health(partner: str, username: str = Depends(get_current_user)):
    health = await db.get_conversation_health(username, partner)
    return ConversationHealth(**health)


@app.get("/api/analytics/conversation/{partner}", response_model=ConversationAnalyticsResult)
async def get_conversation_analytics(partner: str, username: str = Depends(get_current_user)):
    messages = await db.get_conversation_messages(username, partner, limit=1000)
    import ai.conversation_analytics as conversation_analytics
    analytics = conversation_analytics.analyze_conversation(messages)
    return ConversationAnalyticsResult(**analytics)


@app.get("/api/messages/group/{group_name}")
async def get_group_msgs(group_name: str, username: str = Depends(get_current_user)):
    return await db.get_group_messages(group_name)


@app.post("/api/groups")
async def create_group(data: GroupCreate, username: str = Depends(get_current_user)):
    group = await db.create_group(data.name, data.members, username)
    return {"status": "created", "group": group}


@app.get("/api/groups/{target_username}")
async def get_groups(target_username: str, username: str = Depends(get_current_user)):
    if target_username != username:
        raise HTTPException(403, "Access denied")
    return await db.get_user_groups(username)


@app.get("/api/dashboard/stats", response_model=DashboardStats)
async def dashboard_stats(username: str = Depends(get_current_user)):
    return await db.get_dashboard_stats()


@app.get("/api/admin/flagged")
async def admin_flagged(admin: str = Depends(require_admin)):
    return await db.get_flagged_messages()


@app.get("/api/admin/toxic-users")
async def admin_toxic_users(admin: str = Depends(require_admin)):
    stats = await db.get_dashboard_stats()
    return stats["most_toxic_users"]


@app.get("/api/admin/users")
async def admin_users(admin: str = Depends(require_admin)):
    return await db.admin_list_users()

@app.get("/api/admin/analytics/high-risk")
async def admin_high_risk_conversations(admin: str = Depends(require_admin)):
    active_convos = await db.get_active_conversations(limit=20)
    import ai.conversation_analytics as conversation_analytics
    
    results = []
    for conv in active_convos:
        if conv["type"] == "group":
            messages = await db.get_group_messages(conv["name"], limit=100)
            target = conv["name"]
        else:
            messages = await db.get_messages(conv["user1"], conv["user2"], limit=100)
            target = f"{conv['user1']} / {conv['user2']}"
            
        analytics = conversation_analytics.analyze_conversation(messages)
        if analytics["conversation_state"] in ["CRITICAL", "ESCALATING"] or analytics["average_risk_score"] > 40:
            results.append({
                "type": conv["type"],
                "target": target,
                "user1": conv.get("user1"),
                "user2": conv.get("user2"),
                "group_name": conv.get("name"),
                "last_activity": conv["last_activity"],
                "analytics": analytics
            })
            
    # Sort by highest risk first
    results.sort(key=lambda x: x["analytics"]["average_risk_score"], reverse=True)
    return results

@app.get("/api/admin/conversation/{user1}/{user2}")
async def admin_conversation_analytics(user1: str, user2: str, admin: str = Depends(require_admin)):
    messages = await db.get_messages(user1, user2, limit=500)
    import ai.conversation_analytics as conversation_analytics
    analytics = conversation_analytics.analyze_conversation(messages)
    return {"messages": messages, "analytics": analytics}


@app.post("/api/admin/action")
async def admin_user_action(data: AdminAction, admin: str = Depends(require_admin)):
    if data.username == admin and data.action in ("demote_admin",):
        raise HTTPException(400, "Cannot demote yourself")
    success = await db.admin_action(data.username, data.action)
    if not success:
        raise HTTPException(404, "User not found or action failed")
    return {"status": "ok", "username": data.username, "action": data.action}


class ConnectionManager:
    def __init__(self):
        self.active_chats: Dict[str, str] = {}

    async def connect(self, username: str, websocket: WebSocket):
        await websocket.accept()
        is_first = presence.add_connection(username, websocket)
        if is_first:
            await redis_service.set_user_presence(username, True)
            # Broadcast presence_online
            await self.broadcast_system(f"{username} is online", exclude=username)
            await self.broadcast({"type": "presence_online", "username": username}, exclude=username)

    async def disconnect(self, username: str, websocket: WebSocket):
        self.active_chats.pop(username, None)
        is_last = presence.remove_connection(username, websocket)
        if is_last:
            last_seen_ts = datetime.utcnow().isoformat() + "Z"
            await db.update_last_seen(username, last_seen_ts)
            await redis_service.set_user_presence(username, False)
            await self.broadcast_system(f"{username} is offline")
            await self.broadcast({"type": "presence_offline", "username": username, "last_seen": last_seen_ts})

    async def send_to_user(self, username: str, data: dict):
        conns = presence._active_connections.get(username, set())
        dead = []
        for ws in conns:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            presence.remove_connection(username, ws)

    async def broadcast_to_group(self, group_members: list, data: dict, exclude: str = ""):
        for member in group_members:
            if member != exclude:
                await self.send_to_user(member, data)

    async def broadcast(self, data: dict, exclude: str = ""):
        for uname, conns in list(presence._active_connections.items()):
            if uname != exclude:
                for ws in conns:
                    try:
                        await ws.send_json(data)
                    except Exception:
                        pass

    async def broadcast_system(self, message: str, exclude: str = ""):
        data = {"type": "system", "message": message, "timestamp": datetime.utcnow().isoformat()}
        await self.broadcast(data, exclude)


manager = ConnectionManager()


@app.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    try:
        username = verify_token(token)
    except Exception:
        await websocket.close(code=4001)
        return

    await manager.connect(username, websocket)
    users = await db.get_all_users()
    await websocket.send_json({"type": "users_list", "users": users})

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
                msg_type = data.get("type", "message")

                if msg_type == "message":
                    text = data.get("text", "").strip()
                    receiver = data.get("receiver", "")
                    is_group = data.get("is_group", False)
                    force_send = data.get("force_send", False)
                    if not text or not receiver:
                        continue

                    rate = await redis_service.increment_rate(f"msg:{username}")
                    if rate > RATE_LIMIT_MSG:
                        await manager.send_to_user(username, {
                            "type": "error", "message": "Rate limit exceeded. Slow down."
                        })
                        continue

                    is_muted = await db.check_mute(username)
                    if is_muted:
                        await manager.send_to_user(username, {
                            "type": "muted", "message": "You are temporarily muted for toxic behavior."
                        })
                        continue

                    text = sanitize_input(text)
                    recent = await db.get_conversation_messages(username, receiver, limit=10)
                    tox = await ai_manager.analyze_message(text, context=recent)

                    if tox["is_flagged"] and not force_send:
                        from escalation import predict_escalation as calc_escalation
                        esc = calc_escalation(recent, tox["score"], tox["is_flagged"])
                        await manager.send_to_user(username, {
                            "type": "toxicity_pre_send",
                            "message": "This message may be toxic. Review before sending.",
                            "score": tox["score"],
                            "label": tox["label"],
                            "toxic_words": tox.get("toxic_words", []),
                            "rewrite": tox.get("rewrite"),
                            "escalation": esc,
                            "pending_text": text,
                            "receiver": receiver,
                        })
                        continue

                    msg = await db.save_message({
                        "sender": username,
                        "receiver": receiver,
                        "text": text,
                        "is_group": is_group,
                        "toxicity_score": tox["score"],
                        "toxicity_label": tox["label"],
                        "is_flagged": tox["is_flagged"],
                        "toxic_words": tox.get("toxic_words", []),
                        "emotion": tox.get("emotion", "neutral"),
                        "emotion_confidence": tox.get("emotion_confidence", 0.0),
                        "contains_pii": tox.get("contains_pii", False),
                        "pii_entities": tox.get("pii_entities", []),
                        "risk_score": tox.get("risk_score", 0),
                        "risk_level": tox.get("risk_level", "LOW"),
                        "risk_reasons": tox.get("risk_reasons", []),
                        "recommendation": tox.get("recommendation", "Safe to send."),
                        "explanation": tox.get("explanation"),
                        "status": "sent",
                        "reactions": {},
                        "edited": False,
                    })

                    chat_key = f"{min(username, receiver)}:{max(username, receiver)}" if not is_group else f"group:{receiver}"
                    await redis_service.cache_message(chat_key, {
                        "id": msg["id"], "sender": username, "text": text, "timestamp": msg["timestamp"]
                    })

                    payload = {
                        "type": "message",
                        "id": msg["id"],
                        "sender": username,
                        "receiver": receiver,
                        "text": text,
                        "timestamp": msg["timestamp"],
                        "is_group": is_group,
                        "toxicity_score": tox["score"],
                        "toxicity_label": tox["label"],
                        "is_flagged": tox["is_flagged"],
                        "toxic_words": tox.get("toxic_words", []),
                        "emotion": tox.get("emotion", "neutral"),
                        "emotion_confidence": tox.get("emotion_confidence", 0.0),
                        "contains_pii": tox.get("contains_pii", False),
                        "pii_entities": tox.get("pii_entities", []),
                        "risk_score": tox.get("risk_score", 0),
                        "risk_level": tox.get("risk_level", "LOW"),
                        "risk_reasons": tox.get("risk_reasons", []),
                        "recommendation": tox.get("recommendation", "Safe to send."),
                        "explanation": tox.get("explanation"),
                        "status": "sent",
                        "reactions": {},
                        "edited": False,
                    }

                    await manager.send_to_user(username, payload)

                    if is_group:
                        groups = await db.get_user_groups(username)
                        group = next((g for g in groups if g["name"] == receiver), None)
                        if group:
                            await manager.broadcast_to_group(group["members"], payload, exclude=username)
                    else:
                        if presence.is_user_online(receiver):
                            payload["status"] = "delivered"
                            await db.update_message_status(msg["id"], "delivered")
                            await manager.send_to_user(username, {
                                "type": "status_update", "id": msg["id"], "status": "delivered"
                            })
                        if tox["is_flagged"]:
                            await manager.send_to_user(receiver, {
                                "type": "toxicity_warning",
                                "message": "⚠️ Incoming message may contain harmful content",
                                "from": username,
                                "score": tox["score"],
                            })
                        await manager.send_to_user(receiver, payload)

                    if tox["is_flagged"]:
                        warning_result = await db.add_warning(username)
                        await manager.send_to_user(username, {
                            "type": "toxicity_alert",
                            "message": f"Your message was flagged as toxic! Warning {warning_result['warnings']}/3",
                            "score": tox["score"],
                            "label": tox["label"],
                            "warnings": warning_result["warnings"],
                        })
                        if warning_result.get("muted"):
                            await manager.send_to_user(username, {
                                "type": "muted",
                                "message": "You have been muted for 30 minutes due to repeated toxic messages.",
                                "until": warning_result.get("mute_until"),
                            })

                elif msg_type in ["typing_start", "typing_stop"]:
                    receiver = data.get("receiver", "")
                    # Relay event directly to receiver without MongoDB storage
                    await manager.send_to_user(receiver, {"type": msg_type, "sender": username})

                elif msg_type == "active_chat":
                    partner = data.get("partner", "")
                    manager.active_chats[username] = partner

                elif msg_type == "message_delivered":
                    msg_id = data.get("message_id", "")
                    sender = data.get("sender", "")
                    if msg_id:
                        await db.update_message_status(msg_id, "delivered")
                        await manager.send_to_user(sender, {
                            "type": "message_delivered", "message_id": msg_id, "status": "delivered"
                        })

                elif msg_type == "reaction":
                    msg_id = data.get("msg_id", "")
                    emoji = data.get("emoji", "")
                    target = data.get("target", "")
                    if msg_id and emoji:
                        result = await db.add_reaction(msg_id, emoji, username)
                        reaction_payload = {
                            "type": "reaction_update",
                            "msg_id": msg_id,
                            "reactions": result["reactions"],
                            "by": username,
                            "emoji": emoji,
                        }
                        await manager.send_to_user(username, reaction_payload)
                        if target and target != username:
                            await manager.send_to_user(target, reaction_payload)

                elif msg_type == "edit_message":
                    msg_id = data.get("msg_id", "")
                    new_text = data.get("text", "").strip()
                    target = data.get("target", "")
                    
                    if msg_id and new_text:
                        original_msg = await db.get_message_by_id(msg_id)
                        if original_msg and original_msg.get("sender") == username:
                            msg_time = datetime.fromisoformat(original_msg["timestamp"].replace("Z", "+00:00")) if original_msg.get("timestamp") else datetime.utcnow()
                            # 15 minutes edit window (use timezone naive utcnow)
                            if (datetime.utcnow() - msg_time.replace(tzinfo=None)).total_seconds() <= 15 * 60:
                                new_text = sanitize_input(new_text)
                                recent = await db.get_conversation_messages(username, target, limit=10) if target else []
                                tox = await ai_manager.analyze_message(new_text, context=recent)
                                
                                edited_at = datetime.utcnow().isoformat()
                                updates = {
                                    "text": new_text,
                                    "edited": True,
                                    "edited_at": edited_at,
                                    "toxicity_score": tox["score"],
                                    "toxicity_label": tox["label"],
                                    "is_flagged": tox["is_flagged"],
                                    "toxic_words": tox.get("toxic_words", []),
                                    "emotion": tox.get("emotion", "neutral"),
                                    "emotion_confidence": tox.get("emotion_confidence", 0.0),
                                    "contains_pii": tox.get("contains_pii", False),
                                    "pii_entities": tox.get("pii_entities", []),
                                    "risk_score": tox.get("risk_score", 0),
                                    "risk_level": tox.get("risk_level", "LOW"),
                                    "risk_reasons": tox.get("risk_reasons", []),
                                    "recommendation": tox.get("recommendation", "Safe to send."),
                                    "explanation": tox.get("explanation"),
                                }
                                
                                success = await db.update_message_full(msg_id, username, updates)
                                if success:
                                    edit_payload = {
                                        "type": "message_edited",
                                        "msg_id": msg_id,
                                        "by": username,
                                    }
                                    edit_payload.update(updates)
                                    
                                    await manager.send_to_user(username, edit_payload)
                                    if target and target != username:
                                        await manager.send_to_user(target, edit_payload)
                            else:
                                await manager.send_to_user(username, {
                                    "type": "error", "message": "Message edit window (15 minutes) has expired."
                                })
                
                elif msg_type == "delete_message":
                    msg_id = data.get("msg_id", "")
                    target = data.get("target", "")
                    
                    if msg_id:
                        original_msg = await db.get_message_by_id(msg_id)
                        if original_msg:
                            if original_msg.get("deleted"):
                                await manager.send_to_user(username, {
                                    "type": "delete_error", "message": "Message is already deleted."
                                })
                            elif original_msg.get("sender") != username:
                                await manager.send_to_user(username, {
                                    "type": "delete_error", "message": "Cannot delete another user's message."
                                })
                            else:
                                msg_time = datetime.fromisoformat(original_msg["timestamp"].replace("Z", "+00:00")) if original_msg.get("timestamp") else datetime.utcnow()
                                if (datetime.utcnow() - msg_time.replace(tzinfo=None)).total_seconds() <= 15 * 60:
                                    deleted_at = datetime.utcnow().isoformat()
                                    updates = {
                                        "deleted": True,
                                        "deleted_at": deleted_at,
                                        "deleted_by": username
                                    }
                                    success = await db.update_message_full(msg_id, username, updates)
                                    if success:
                                        delete_payload = {
                                            "type": "message_deleted",
                                            "message_id": msg_id,
                                            "deleted": True,
                                            "deleted_at": deleted_at
                                        }
                                        await manager.send_to_user(username, delete_payload)
                                        if target and target != username:
                                            await manager.send_to_user(target, delete_payload)
                                else:
                                    await manager.send_to_user(username, {
                                        "type": "delete_error", "message": "Message delete window (15 minutes) has expired."
                                    })
                                    
                elif msg_type == "message_read":
                    msg_id = data.get("msg_id", "")
                    sender = data.get("sender", "")
                    
                    if msg_id and sender:
                        original_msg = await db.get_message_by_id(msg_id)
                        if original_msg:
                            # Only the receiver can mark the message as read
                            if original_msg.get("receiver") == username:
                                if original_msg.get("status") != "read":
                                    read_at = datetime.utcnow().isoformat()
                                    updates = {
                                        "status": "read",
                                        "read_at": read_at
                                    }
                                    # the message belongs to `sender`, so we must pass sender to update_message_full
                                    success = await db.update_message_full(msg_id, sender, updates)
                                    if success:
                                        read_payload = {
                                            "type": "message_read",
                                            "message_id": msg_id,
                                            "status": "read",
                                            "read_at": read_at
                                        }
                                        # Send back to receiver (in case they have multiple tabs)
                                        await manager.send_to_user(username, read_payload)
                                        # Send to original sender so they see the blue ticks
                                        await manager.send_to_user(sender, read_payload)
                            
                elif msg_type == "get_users":
                    users = await db.get_all_users()
                    await websocket.send_json({"type": "users_list", "users": users})

            except Exception as inner_e:
                import traceback
                traceback.print_exc()
                await manager.send_to_user(username, {
                    "type": "error", "message": f"Internal server error: {inner_e}"
                })

    except WebSocketDisconnect:
        await manager.disconnect(username, websocket)
    except Exception as e:
        print(f"WebSocket fatal error for {username}: {e}")
        await manager.disconnect(username, websocket)


@app.get("/")
async def health():
    import ai_model
    return {
        "app": "ToxiChat Pro",
        "version": "3.0.0",
        "status": "running",
        "ml_model": "transformer" if ai_model.is_transformer_ready() else "keywords",
        "storage": "MongoDB" if not db.is_memory_mode() else "In-Memory ⚠️",
    }

@app.get("/api/ai/health")
async def ai_health(username: str = Depends(get_current_user)):
    import ai.resilience as resilience
    return resilience.get_ai_health()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=True)

