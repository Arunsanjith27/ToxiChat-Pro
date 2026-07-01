import os
import json
from datetime import datetime
from typing import Dict
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

from models import (
    UserRegister, UserLogin, TokenOut, UserOut,
    ToxicityRequest, ToxicityResult, DashboardStats, GroupCreate, RewriteRequest,
    ForgotPasswordRequest, ResetPasswordRequest, ProfileUpdate,
    EscalationRequest, EscalationResult, AdminAction, ConversationHealth,
)
import database as db
import ai.manager as ai_manager
import redis_service
from security import hash_password, verify_password, migrate_password, sanitize_input, validate_file
from auth import (
    create_token, verify_token, get_current_user, require_admin, is_admin_user,
)

RATE_LIMIT_MSG = int(os.getenv("RATE_LIMIT_MSG", "30"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
AVATAR_DIR = os.path.join(os.path.dirname(__file__), "uploads", "avatars")
os.makedirs(AVATAR_DIR, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.get_db()
    await redis_service.init_redis()
    print("[OK] ToxiChat Pro API ready")
    yield


app = FastAPI(title="ToxiChat Pro API", version="3.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS if CORS_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "uploads")), name="uploads")


def _token_response(user: dict) -> TokenOut:
    return TokenOut(
        access_token=create_token(user["username"], is_admin_user(user["username"], user)),
        username=user["username"],
        display_name=user.get("display_name", user["username"]),
        role=user.get("role", "user"),
        avatar_url=user.get("avatar_url"),
        reputation_score=user.get("reputation_score", 100),
    )


@app.post("/api/register", response_model=TokenOut)
async def register(data: UserRegister):
    existing = await db.get_user(data.username)
    if existing:
        raise HTTPException(400, "Username already taken")
    hashed = hash_password(data.password)
    display = data.display_name or data.username
    user = await db.create_user(data.username, hashed, display, data.email)
    return _token_response(user)


@app.post("/api/login", response_model=TokenOut)
async def login(data: UserLogin):
    user = await db.get_user(data.username)
    if not user:
        raise HTTPException(401, "Invalid username or password")
    if not verify_password(data.password, user["password"]):
        new_hash = migrate_password(data.password, user["password"])
        if new_hash:
            await db.update_user_password(data.username, new_hash)
        else:
            raise HTTPException(401, "Invalid username or password")
    else:
        new_hash = migrate_password(data.password, user["password"])
        if new_hash:
            await db.update_user_password(data.username, new_hash)
    return _token_response(user)


@app.post("/api/auth/forgot-password")
async def forgot_password(data: ForgotPasswordRequest):
    token = await db.create_reset_token(data.username)
    if not token:
        return {"message": "If the account exists, a reset link has been generated", "token": None}
    return {
        "message": "Password reset token generated. Use it within 1 hour.",
        "token": token,
        "reset_url_hint": f"/reset-password?token={token}",
    }


@app.post("/api/auth/reset-password")
async def reset_password(data: ResetPasswordRequest):
    username = await db.consume_reset_token(data.token)
    if not username:
        raise HTTPException(400, "Invalid or expired reset token")
    await db.update_user_password(username, hash_password(data.new_password))
    user = await db.get_user(username)
    return {"message": "Password updated successfully", "username": username}


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


@app.post("/api/predict", response_model=ToxicityResult)
async def predict(data: ToxicityRequest, username: str = Depends(get_current_user)):
    result = await ai_manager.analyze_message(data.text)
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
        rewrite=result.get("rewrite"),
        escalation=esc,
        conversation_health=esc["conversation_health"],
    )


@app.post("/api/rewrite")
async def rewrite(data: RewriteRequest, username: str = Depends(get_current_user)):
    import ml_service
    result = ml_service.rewrite_toxic(data.text)
    return {"original": data.text, "rewritten": result}


@app.get("/api/search")
async def search_messages(q: str = "", limit: int = 50, username: str = Depends(get_current_user)):
    return await db.search_messages(q, limit)


@app.get("/api/messages/{user1}/{user2}")
async def get_messages(user1: str, user2: str, username: str = Depends(get_current_user)):
    if username not in (user1, user2):
        raise HTTPException(403, "Access denied to this conversation")
    return await db.get_messages(user1, user2)


@app.get("/api/conversation/health/{partner}", response_model=ConversationHealth)
async def conversation_health(partner: str, username: str = Depends(get_current_user)):
    health = await db.get_conversation_health(username, partner)
    return ConversationHealth(**health)


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
        self.connections: Dict[str, WebSocket] = {}
        self.active_chats: Dict[str, str] = {}

    async def connect(self, username: str, websocket: WebSocket):
        await websocket.accept()
        self.connections[username] = websocket
        await db.set_user_online(username, True)
        await redis_service.set_user_presence(username, True)
        await self.broadcast_system(f"{username} is online", exclude=username)

    async def disconnect(self, username: str):
        self.connections.pop(username, None)
        self.active_chats.pop(username, None)
        await db.set_user_online(username, False)
        await redis_service.set_user_presence(username, False)
        await self.broadcast_system(f"{username} is offline")

    async def send_to_user(self, username: str, data: dict):
        ws = self.connections.get(username)
        if ws:
            try:
                await ws.send_json(data)
            except Exception:
                self.connections.pop(username, None)

    async def broadcast_to_group(self, group_members: list, data: dict, exclude: str = ""):
        for member in group_members:
            if member != exclude:
                await self.send_to_user(member, data)

    async def broadcast_system(self, message: str, exclude: str = ""):
        data = {"type": "system", "message": message, "timestamp": datetime.utcnow().isoformat()}
        for uname, ws in list(self.connections.items()):
            if uname != exclude:
                try:
                    await ws.send_json(data)
                except Exception:
                    self.connections.pop(uname, None)


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
                        if receiver in manager.connections:
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

                elif msg_type == "typing":
                    receiver = data.get("receiver", "")
                    await redis_service.set_typing(username, receiver)
                    await manager.send_to_user(receiver, {"type": "typing", "sender": username})

                elif msg_type == "active_chat":
                    partner = data.get("partner", "")
                    manager.active_chats[username] = partner

                elif msg_type == "seen":
                    msg_id = data.get("id", "")
                    sender = data.get("sender", "")
                    if msg_id:
                        await db.update_message_status(msg_id, "seen")
                        await manager.send_to_user(sender, {
                            "type": "status_update", "id": msg_id, "status": "seen"
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
                        success = await db.update_message_text(msg_id, new_text, username)
                        if success:
                            edit_payload = {
                                "type": "message_edited",
                                "msg_id": msg_id,
                                "text": new_text,
                                "by": username,
                            }
                            await manager.send_to_user(username, edit_payload)
                            if target and target != username:
                                await manager.send_to_user(target, edit_payload)

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
        await manager.disconnect(username)
    except Exception as e:
        print(f"WebSocket fatal error for {username}: {e}")
        await manager.disconnect(username)


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=True)
