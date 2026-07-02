import datetime
import uuid
import asyncio
from typing import Optional, List
from database import get_db

async def log_event(
    actor_username: str,
    action: str,
    resource_type: str,
    resource_id: str,
    actor_role: str = "MODERATOR",
    actor_id: str = "SYSTEM",
    incident_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
    status: str = "SUCCESS",
    description: str = "",
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    metadata: dict = None
):
    """
    Centralized, immutable audit logger. 
    Execution should be spun off as an async background task to prevent blocking.
    """
    if metadata is None:
        metadata = {}

    entry = {
        "audit_id": str(uuid.uuid4()),
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "actor_id": actor_id,
        "actor_username": actor_username,
        "actor_role": actor_role,
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "incident_id": incident_id,
        "conversation_id": conversation_id,
        "status": status,
        "description": description,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "metadata": metadata,
        "version": "1.0"
    }

    # Fire and forget database insertion
    asyncio.create_task(_insert_log(entry))

async def _insert_log(entry: dict):
    try:
        db = await get_db()
        await db.audit_logs.insert_one(entry)
    except Exception as e:
        print(f"[AUDIT LOG ERROR] Failed to record event: {str(e)}")

async def get_audit_logs(limit: int = 100, action: str = None, actor: str = None) -> List[dict]:
    db = await get_db()
    query = {}
    if action: query["action"] = action
    if actor: query["actor_username"] = actor
    
    cursor = db.audit_logs.find(query, {"_id": 0}).sort("timestamp", -1)
    return await cursor.to_list(length=limit)

async def get_incident_history(incident_id: str) -> List[dict]:
    db = await get_db()
    cursor = db.audit_logs.find({"incident_id": incident_id}, {"_id": 0}).sort("timestamp", 1)
    return await cursor.to_list(length=100)

async def get_user_activity(username: str, limit: int = 50) -> List[dict]:
    db = await get_db()
    cursor = db.audit_logs.find({"actor_username": username}, {"_id": 0}).sort("timestamp", -1)
    return await cursor.to_list(length=limit)

async def search_audit_logs(filters: dict, limit: int = 100) -> List[dict]:
    db = await get_db()
    cursor = db.audit_logs.find(filters, {"_id": 0}).sort("timestamp", -1)
    return await cursor.to_list(length=limit)
