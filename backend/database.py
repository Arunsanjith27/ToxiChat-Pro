import os
import asyncio
import secrets
from datetime import datetime, timedelta
from typing import Optional, List

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except ImportError:
    pass

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "toxichat")

_db = None
_client = None
_use_memory = False
_memory_store = {"users": [], "messages": [], "groups": [], "reset_tokens": []}
MAX_RETRIES = 3
RETRY_DELAY = 2


def _needs_tls(mongo_url: str) -> bool:
    return mongo_url.startswith("mongodb+srv://") or "tls=true" in mongo_url.lower()


async def get_db():
    global _db, _client, _use_memory
    if _db is not None and _db != "memory":
        return _db
    if _use_memory:
        return None

    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            kwargs = {
                "serverSelectionTimeoutMS": 5000,
                "connectTimeoutMS": 5000,
                "socketTimeoutMS": 10000,
            }
            if _needs_tls(MONGO_URL):
                import certifi
                kwargs["tlsCAFile"] = certifi.where()
            _client = AsyncIOMotorClient(MONGO_URL, **kwargs)
            await _client.admin.command("ping")
            _db = _client[DB_NAME]
            _use_memory = False
            await _db.users.create_index("username", unique=True)
            await _db.messages.create_index("timestamp")
            await _db.messages.create_index("is_flagged")
            await _db.messages.create_index([("sender", 1), ("receiver", 1)])
            await _db.messages.create_index([("sender", 1), ("receiver", 1), ("timestamp", -1)])
            await _db.reset_tokens.create_index("token", unique=True)
            await _db.reset_tokens.create_index("expires_at", expireAfterSeconds=0)
            print(f"✅ MongoDB connected: {DB_NAME} (attempt {attempt})")
            return _db
        except Exception as e:
            last_err = e
            print(f"⚠️ MongoDB attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES:
                await asyncio.sleep(RETRY_DELAY)

    print(f"❌ MongoDB unavailable after {MAX_RETRIES} attempts — using in-memory storage")
    print(f"❌ WARNING: Data will NOT persist across restarts!")
    _use_memory = True
    _db = "memory"
    return None


def is_memory_mode():
    return _use_memory


async def create_user(username: str, hashed_password: str, display_name: str, email: str = None) -> dict:
    admin_names = {
        u.strip().lower()
        for u in os.getenv("ADMIN_USERNAMES", "admin").split(",")
        if u.strip()
    }
    user = {
        "username": username,
        "password": hashed_password,
        "display_name": display_name,
        "email": email,
        "created_at": datetime.utcnow().isoformat(),
        "is_online": False,
        "warnings_count": 0,
        "is_muted": False,
        "mute_until": None,
        "mute_history": [],
        "avatar_url": None,
        "bio": "",
        "reputation_score": 100,
        "reputation_tier": "excellent",
        "role": "admin" if username.lower() in admin_names else "user",
        "total_messages": 0,
        "toxic_messages": 0,
    }
    if _use_memory:
        if any(u["username"] == username for u in _memory_store["users"]):
            raise ValueError("Username already exists")
        _memory_store["users"].append(user)
    else:
        db = await get_db()
        await db.users.insert_one(user.copy())
    return user


async def get_user(username: str) -> Optional[dict]:
    if _use_memory:
        return next((u for u in _memory_store["users"] if u["username"] == username), None)
    db = await get_db()
    return await db.users.find_one({"username": username}, {"_id": 0})


async def update_user_password(username: str, new_hash: str):
    if _use_memory:
        for u in _memory_store["users"]:
            if u["username"] == username:
                u["password"] = new_hash
    else:
        db = await get_db()
        await db.users.update_one({"username": username}, {"$set": {"password": new_hash}})


async def set_user_online(username: str, online: bool):
    if _use_memory:
        for u in _memory_store["users"]:
            if u["username"] == username:
                u["is_online"] = online
    else:
        db = await get_db()
        await db.users.update_one({"username": username}, {"$set": {"is_online": online}})


async def get_all_users() -> List[dict]:
    if _use_memory:
        return [{
            "username": u["username"],
            "display_name": u["display_name"],
            "is_online": u.get("is_online", False),
            "warnings_count": u.get("warnings_count", 0),
            "is_muted": u.get("is_muted", False),
            "avatar_url": u.get("avatar_url"),
            "reputation_score": u.get("reputation_score", 100),
            "reputation_tier": u.get("reputation_tier", "excellent"),
            "role": u.get("role", "user"),
        } for u in _memory_store["users"]]
    db = await get_db()
    cursor = db.users.find({}, {
        "_id": 0, "password": 0, "mute_history": 0, "email": 0
    })
    return await cursor.to_list(length=500)


async def add_warning(username: str) -> dict:
    user = await get_user(username)
    if not user:
        return {"warnings": 0, "muted": False}
    count = user.get("warnings_count", 0) + 1
    muted = count >= 3
    mute_until = (datetime.utcnow() + timedelta(minutes=30)).isoformat() if muted else None
    mute_entry = {"at": datetime.utcnow().isoformat(), "warnings": count}
    if _use_memory:
        for u in _memory_store["users"]:
            if u["username"] == username:
                u["warnings_count"] = count
                u["is_muted"] = muted
                u["mute_until"] = mute_until
                u.setdefault("mute_history", []).append(mute_entry)
    else:
        db = await get_db()
        await db.users.update_one({"username": username}, {
            "$set": {"warnings_count": count, "is_muted": muted, "mute_until": mute_until},
            "$push": {"mute_history": mute_entry}
        })
    return {"warnings": count, "muted": muted, "mute_until": mute_until}


async def check_mute(username: str) -> bool:
    user = await get_user(username)
    if not user or not user.get("is_muted"):
        return False
    mute_until = user.get("mute_until")
    if mute_until and datetime.fromisoformat(mute_until) < datetime.utcnow():
        if _use_memory:
            for u in _memory_store["users"]:
                if u["username"] == username:
                    u["is_muted"] = False
                    u["mute_until"] = None
        else:
            db = await get_db()
            await db.users.update_one({"username": username}, {"$set": {"is_muted": False, "mute_until": None}})
        return False
    return True


async def save_message(msg: dict) -> dict:
    msg["timestamp"] = datetime.utcnow().isoformat()
    msg["id"] = f"msg_{datetime.utcnow().timestamp()}"
    msg.setdefault("status", "sent")
    msg.setdefault("toxic_words", [])
    if _use_memory:
        _memory_store["messages"].append(msg)
    else:
        db = await get_db()
        await db.messages.insert_one(msg.copy())
    sender = msg.get("sender")
    if sender:
        await _increment_user_message_stats(sender, msg.get("is_flagged", False))
    return msg


async def _increment_user_message_stats(username: str, is_flagged: bool):
    from escalation import compute_reputation
    user = await get_user(username)
    if not user:
        return
    total = user.get("total_messages", 0) + 1
    toxic = user.get("toxic_messages", 0) + (1 if is_flagged else 0)
    rep = compute_reputation(total, toxic, user.get("warnings_count", 0), len(user.get("mute_history", [])))
    updates = {
        "total_messages": total,
        "toxic_messages": toxic,
        "reputation_score": rep["reputation_score"],
        "reputation_tier": rep["reputation_tier"],
    }
    if _use_memory:
        for u in _memory_store["users"]:
            if u["username"] == username:
                u.update(updates)
    else:
        db = await get_db()
        await db.users.update_one({"username": username}, {"$set": updates})


async def update_message_status(msg_id: str, status: str):
    if _use_memory:
        for m in _memory_store["messages"]:
            if m.get("id") == msg_id:
                m["status"] = status
    else:
        db = await get_db()
        await db.messages.update_one({"id": msg_id}, {"$set": {"status": status}})


async def get_messages(user1: str, user2: str, limit: int = 50) -> List[dict]:
    if _use_memory:
        msgs = [m for m in _memory_store["messages"]
                if not m.get("is_group") and
                ((m["sender"] == user1 and m["receiver"] == user2) or
                 (m["sender"] == user2 and m["receiver"] == user1))]
        return msgs[-limit:]
    db = await get_db()
    cursor = db.messages.find(
        {"$or": [
            {"sender": user1, "receiver": user2, "is_group": False},
            {"sender": user2, "receiver": user1, "is_group": False}
        ]}, {"_id": 0}
    ).sort("timestamp", -1).limit(limit)
    msgs = await cursor.to_list(length=limit)
    return list(reversed(msgs))


async def get_group_messages(group: str, limit: int = 50) -> List[dict]:
    if _use_memory:
        msgs = [m for m in _memory_store["messages"]
                if m.get("is_group") and m["receiver"] == group]
        return msgs[-limit:]
    db = await get_db()
    cursor = db.messages.find(
        {"receiver": group, "is_group": True}, {"_id": 0}
    ).sort("timestamp", -1).limit(limit)
    msgs = await cursor.to_list(length=limit)
    return list(reversed(msgs))


async def get_flagged_messages(limit: int = 50) -> List[dict]:
    if _use_memory:
        return [m for m in _memory_store["messages"] if m.get("is_flagged")][-limit:]
    db = await get_db()
    cursor = db.messages.find({"is_flagged": True}, {"_id": 0}).sort("timestamp", -1).limit(limit)
    return await cursor.to_list(length=limit)


async def get_dashboard_stats() -> dict:
    if _use_memory:
        msgs = _memory_store["messages"]
        all_users = _memory_store["users"]
    else:
        db = await get_db()
        msgs = await db.messages.find({}, {"_id": 0}).to_list(length=10000)
        all_users = await db.users.find({}, {"_id": 0, "password": 0}).to_list(length=5000)

    total = len(msgs)
    toxic = sum(1 for m in msgs if m.get("is_flagged", False))
    non_toxic = total - toxic
    
    total_risk = 0
    total_toxicity = 0
    risk_dist = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    rewrite_attempts = 0
    rewrite_successes = 0
    
    for m in msgs:
        total_risk += m.get("risk_score", 0)
        total_toxicity += m.get("toxicity_score", 0.0)
        lvl = m.get("risk_level", "LOW")
        if lvl in risk_dist:
            risk_dist[lvl] += 1
            
        if m.get("is_flagged", False):
            rewrite_attempts += 1
            if m.get("rewrite"):
                rewrite_successes += 1

    user_toxic = {}
    for m in msgs:
        if m.get("is_flagged"):
            user_toxic[m["sender"]] = user_toxic.get(m["sender"], 0) + 1
    top_users = sorted(user_toxic.items(), key=lambda x: x[1], reverse=True)[:10]
    top_users = [{"username": u, "toxic_count": c} for u, c in top_users]

    hourly = {}
    daily = {}
    for m in msgs:
        try:
            dt = datetime.fromisoformat(m["timestamp"])
            h = dt.hour
            d = dt.strftime("%Y-%m-%d")
        except Exception:
            h, d = 0, "unknown"
        if h not in hourly:
            hourly[h] = {"hour": h, "total": 0, "toxic": 0}
        hourly[h]["total"] += 1
        if m.get("is_flagged"):
            hourly[h]["toxic"] += 1
        if d not in daily:
            daily[d] = {"date": d, "total": 0, "toxic": 0}
        daily[d]["total"] += 1
        if m.get("is_flagged"):
            daily[d]["toxic"] += 1

    flagged = [{"sender": m.get("sender"), "text": m.get("text", "")[:100],
                "score": m.get("toxicity_score", 0), "timestamp": m.get("timestamp")}
               for m in msgs if m.get("is_flagged")][-20:]

    from escalation import predict_escalation
    conv_keys = set()
    health_scores = []
    escalation_events = 0
    critical_convs = []
    
    for m in msgs:
        if m.get("is_group"):
            continue
        pair = tuple(sorted([m.get("sender", ""), m.get("receiver", "")]))
        conv_keys.add(pair)
        
    for u1, u2 in list(conv_keys)[:50]:
        conv_msgs = [m for m in msgs if not m.get("is_group") and
                     ((m["sender"] == u1 and m["receiver"] == u2) or
                      (m["sender"] == u2 and m["receiver"] == u1))]
        if conv_msgs:
            esc = predict_escalation(conv_msgs[-10:], 0, False)
            health_scores.append(esc["conversation_health"])
            if esc["is_escalating"]:
                escalation_events += 1
                
            # Check if critical conversation
            if any(m.get("risk_level") == "CRITICAL" for m in conv_msgs[-10:]):
                critical_convs.append({"participants": [u1, u2], "health": esc["conversation_health"]})

    return {
        "total_messages": total,
        "toxic_count": toxic,
        "non_toxic_count": non_toxic,
        "toxicity_rate": round(toxic / max(total, 1), 4),
        "total_users": len(all_users),
        "online_users": sum(1 for u in all_users if u.get("is_online")),
        "most_toxic_users": top_users,
        "hourly_trend": sorted(hourly.values(), key=lambda x: x["hour"]),
        "daily_trend": sorted(daily.values(), key=lambda x: x["date"]),
        "flagged_messages": flagged,
        "conversation_health_avg": round(sum(health_scores) / max(len(health_scores), 1), 1),
        "escalation_events": escalation_events,
        "risk_distribution": risk_dist,
        "critical_conversations": critical_convs,
        "average_risk": round(total_risk / max(total, 1), 1),
        "average_toxicity": round(total_toxicity / max(total, 1), 2),
        "rewrite_success_rate": round(rewrite_successes / max(rewrite_attempts, 1) * 100, 1),
    }


async def create_group(name: str, members: List[str], creator: str) -> dict:
    group = {"name": name, "members": list(set(members + [creator])), "creator": creator,
             "created_at": datetime.utcnow().isoformat()}
    if _use_memory:
        _memory_store["groups"].append(group)
    else:
        db = await get_db()
        await db.groups.insert_one(group.copy())
    return group


async def get_user_groups(username: str) -> List[dict]:
    if _use_memory:
        return [g for g in _memory_store["groups"] if username in g.get("members", [])]
    db = await get_db()
    cursor = db.groups.find({"members": username}, {"_id": 0})
    return await cursor.to_list(length=100)


async def search_messages(query: str, limit: int = 50) -> List[dict]:
    if not query or not query.strip():
        return []
    if _use_memory:
        q = query.strip().lower()
        results = [m for m in _memory_store["messages"]
                   if q in m.get("text", "").lower() or q in m.get("sender", "").lower()]
        return results[-limit:]
    db = await get_db()
    cursor = db.messages.find(
        {"text": {"$regex": query.strip(), "$options": "i"}},
        {"_id": 0}
    ).sort("timestamp", -1).limit(limit)
    return await cursor.to_list(length=limit)


async def add_reaction(msg_id: str, emoji: str, username: str) -> dict:
    if _use_memory:
        for m in _memory_store["messages"]:
            if m.get("id") == msg_id:
                reactions = m.setdefault("reactions", {})
                users = reactions.setdefault(emoji, [])
                if username in users:
                    users.remove(username)
                    if not users:
                        del reactions[emoji]
                else:
                    users.append(username)
                return {"reactions": m.get("reactions", {})}
        return {"reactions": {}}
    db = await get_db()
    doc = await db.messages.find_one({"id": msg_id}, {"_id": 0, "reactions": 1})
    reactions = (doc or {}).get("reactions", {})
    users = reactions.get(emoji, [])
    if username in users:
        users.remove(username)
        if not users and emoji in reactions:
            del reactions[emoji]
    else:
        users.append(username)
        reactions[emoji] = users
    await db.messages.update_one({"id": msg_id}, {"$set": {"reactions": reactions}})
    return {"reactions": reactions}


async def update_message_text(msg_id: str, new_text: str, username: str) -> bool:
    if _use_memory:
        for m in _memory_store["messages"]:
            if m.get("id") == msg_id and m.get("sender") == username:
                m["text"] = new_text
                m["edited"] = True
                return True
        return False
    db = await get_db()
    result = await db.messages.update_one(
        {"id": msg_id, "sender": username},
        {"$set": {"text": new_text, "edited": True}}
    )
    return result.modified_count > 0


async def update_user_profile(username: str, updates: dict) -> Optional[dict]:
    allowed = {"display_name", "avatar_url", "bio"}
    filtered = {k: v for k, v in updates.items() if k in allowed and v is not None}
    if not filtered:
        return await get_user(username)
    if _use_memory:
        for u in _memory_store["users"]:
            if u["username"] == username:
                u.update(filtered)
                return {k: u.get(k) for k in ["username", "display_name", "avatar_url", "bio", "reputation_score", "reputation_tier", "role"]}
        return None
    db = await get_db()
    await db.users.update_one({"username": username}, {"$set": filtered})
    return await db.users.find_one({"username": username}, {
        "_id": 0, "password": 0, "mute_history": 0, "email": 0
    })


async def create_reset_token(username: str) -> Optional[str]:
    user = await get_user(username)
    if not user:
        return None
    token = secrets.token_urlsafe(32)
    expires = datetime.utcnow() + timedelta(hours=1)
    doc = {"token": token, "username": username, "expires_at": expires}
    if _use_memory:
        _memory_store["reset_tokens"] = [
            t for t in _memory_store["reset_tokens"]
            if t["username"] != username
        ]
        _memory_store["reset_tokens"].append({
            **doc, "expires_at": expires.isoformat()
        })
    else:
        db = await get_db()
        await db.reset_tokens.delete_many({"username": username})
        await db.reset_tokens.insert_one(doc)
    return token


async def consume_reset_token(token: str) -> Optional[str]:
    if _use_memory:
        for t in _memory_store["reset_tokens"]:
            if t["token"] == token:
                if datetime.fromisoformat(t["expires_at"]) < datetime.utcnow():
                    return None
                _memory_store["reset_tokens"] = [
                    x for x in _memory_store["reset_tokens"] if x["token"] != token
                ]
                return t["username"]
        return None
    db = await get_db()
    doc = await db.reset_tokens.find_one_and_delete({"token": token})
    if not doc:
        return None
    if doc["expires_at"] < datetime.utcnow():
        return None
    return doc["username"]


async def get_conversation_messages(user1: str, user2: str, limit: int = 20) -> List[dict]:
    return await get_messages(user1, user2, limit)


async def get_conversation_health(user1: str, user2: str) -> dict:
    from escalation import predict_escalation
    msgs = await get_messages(user1, user2, limit=20)
    if not msgs:
        return {
            "partner": user2,
            "health_score": 100,
            "escalation_level": "low",
            "trend": "stable",
            "total_messages": 0,
            "toxic_messages": 0,
        }
    toxic = sum(1 for m in msgs if m.get("is_flagged"))
    esc = predict_escalation(msgs, 0, False)
    return {
        "partner": user2,
        "health_score": esc["conversation_health"],
        "escalation_level": esc["escalation_level"],
        "trend": esc["trend"],
        "total_messages": len(msgs),
        "toxic_messages": toxic,
    }


async def admin_list_users() -> List[dict]:
    if _use_memory:
        return [{
            "username": u["username"],
            "display_name": u.get("display_name"),
            "warnings_count": u.get("warnings_count", 0),
            "is_muted": u.get("is_muted", False),
            "reputation_score": u.get("reputation_score", 100),
            "reputation_tier": u.get("reputation_tier", "excellent"),
            "role": u.get("role", "user"),
            "total_messages": u.get("total_messages", 0),
            "toxic_messages": u.get("toxic_messages", 0),
            "is_online": u.get("is_online", False),
        } for u in _memory_store["users"]]
    db = await get_db()
    cursor = db.users.find({}, {
        "_id": 0, "password": 0, "mute_history": 0, "email": 0
    }).sort("reputation_score", 1)
    return await cursor.to_list(length=500)


async def admin_action(username: str, action: str) -> bool:
    user = await get_user(username)
    if not user:
        return False
    updates = {}
    if action == "unmute":
        updates = {"is_muted": False, "mute_until": None}
    elif action == "reset_warnings":
        updates = {"warnings_count": 0, "is_muted": False, "mute_until": None}
    elif action == "promote_admin":
        updates = {"role": "admin"}
    elif action == "demote_admin":
        updates = {"role": "user"}
    else:
        return False
    if _use_memory:
        for u in _memory_store["users"]:
            if u["username"] == username:
                u.update(updates)
                return True
        return False
    db = await get_db()
    result = await db.users.update_one({"username": username}, {"$set": updates})
    return result.modified_count > 0 or bool(updates)
