import datetime
import uuid
from typing import List, Dict, Any, Optional
from database import get_db

import ai.manager as ai_manager
import ai.conversation_analytics as conversation_analytics
import audit

async def create_incident(conversation_id: str, priority: str, created_by: str, participants: Optional[List[str]] = None, is_group: Optional[bool] = None) -> dict:
    """
    Creates an immutable incident snapshot from a conversation.
    """
    from database import get_db, get_messages_for_conversation
    db = await get_db()
    
    # 1. Fetch Conversation History
    messages = await get_messages_for_conversation(db, conversation_id, participants, is_group, limit=100)
        
    if not messages:
        raise ValueError("Cannot create incident: Conversation not found or empty.")

    # 2. Generate Immutable Evidence Snapshots
    analytics_snapshot = conversation_analytics.analyze_conversation(messages)
    
    # Normally we would fetch the exact cached prediction, but we generate it here for the snapshot
    import ai.escalation_engine as escalation_engine
    prediction_snapshot = escalation_engine.predict_escalation(messages, analytics_snapshot)
    
    # Also fetch a copilot summary snapshot for the incident brief
    import ai.copilot_context as copilot_context
    import ai.moderator_copilot as moderator_copilot
    ctx = copilot_context.build_copilot_context(messages)
    copilot_snapshot = moderator_copilot.answer_moderator_query("Summarize this incident.", ctx)
    
    now_iso = datetime.datetime.utcnow().isoformat()
    incident_id = str(uuid.uuid4())
    resolved_is_group = is_group if is_group is not None else (messages[0].get("is_group", False) if messages else False)
    
    print("MESSAGES SENDERS:", [m.get("sender") for m in messages])
    print("MESSAGES SENDERS TYPES:", [type(m.get("sender")) for m in messages])
    
    # 3. Construct Incident Document
    incident = {
        "incident_id": incident_id,
        "conversation_id": conversation_id,
        "created_at": now_iso,
        "updated_at": now_iso,
        "status": "OPEN",
        "priority": priority,
        "assigned_to": None,
        "created_by": created_by,
        "resolved_by": None,
        "resolved_at": None,
        "prediction_snapshot": prediction_snapshot,
        "analytics_snapshot": analytics_snapshot,
        "copilot_snapshot": copilot_snapshot,
        "tags": [analytics_snapshot.get("conversation_state", "UNKNOWN")],
        "metadata": {
            "message_count": len(messages),
            "participants": list(set([m["sender"] for m in messages if not isinstance(m.get("sender"), list)])),
            "is_group": resolved_is_group
        }
    }
    
    await db.incidents.insert_one(incident)
    del incident["_id"] # Remove mongo internal ID before returning
    
    await audit.log_event(
        actor_username=created_by,
        action="INCIDENT_CREATED",
        resource_type="INCIDENT",
        resource_id=incident_id,
        incident_id=incident_id,
        conversation_id=conversation_id,
        description=f"Incident {incident_id} created with priority {priority}"
    )
    return incident

async def list_incidents(status: Optional[str] = None, priority: Optional[str] = None) -> List[dict]:
    db = await get_db()
    query = {}
    if status: query["status"] = status
    if priority: query["priority"] = priority
    
    cursor = db.incidents.find(query, {"_id": 0}).sort("created_at", -1)
    return await cursor.to_list(length=100)

async def get_incident(incident_id: str) -> dict:
    db = await get_db()
    incident = await db.incidents.find_one({"incident_id": incident_id}, {"_id": 0})
    if not incident:
        raise ValueError("Incident not found.")
    return incident

async def assign_incident(incident_id: str, assignee: str, assigned_by: str) -> dict:
    db = await get_db()
    now_iso = datetime.datetime.utcnow().isoformat()
    
    update_data = {
        "assigned_to": assignee,
        "updated_at": now_iso,
        "status": "UNDER_INVESTIGATION" # Auto-transition state
    }
    
    result = await db.incidents.update_one(
        {"incident_id": incident_id},
        {"$set": update_data}
    )
    if result.matched_count == 0:
        raise ValueError("Incident not found.")
        
    await audit.log_event(
        actor_username=assigned_by,
        action="INCIDENT_ASSIGNED",
        resource_type="INCIDENT",
        resource_id=incident_id,
        incident_id=incident_id,
        description=f"Incident assigned to {assignee}"
    )
        
    return await get_incident(incident_id)

async def update_status(incident_id: str, status: str) -> dict:
    db = await get_db()
    now_iso = datetime.datetime.utcnow().isoformat()
    
    result = await db.incidents.update_one(
        {"incident_id": incident_id},
        {"$set": {"status": status, "updated_at": now_iso}}
    )
    if result.matched_count == 0:
        raise ValueError("Incident not found.")
        
    await audit.log_event(
        actor_username="SYSTEM", # Should be passed by the user calling, but we'll default to SYSTEM
        action="STATUS_CHANGED",
        resource_type="INCIDENT",
        resource_id=incident_id,
        incident_id=incident_id,
        description=f"Incident status changed to {status}"
    )
        
    return await get_incident(incident_id)

async def resolve_incident(incident_id: str, resolved_by: str) -> dict:
    db = await get_db()
    now_iso = datetime.datetime.utcnow().isoformat()
    
    update_data = {
        "status": "RESOLVED",
        "resolved_by": resolved_by,
        "resolved_at": now_iso,
        "updated_at": now_iso
    }
    
    result = await db.incidents.update_one(
        {"incident_id": incident_id},
        {"$set": update_data}
    )
    if result.matched_count == 0:
        raise ValueError("Incident not found.")
        
    await audit.log_event(
        actor_username=resolved_by,
        action="INCIDENT_RESOLVED",
        resource_type="INCIDENT",
        resource_id=incident_id,
        incident_id=incident_id,
        description=f"Incident resolved"
    )
        
    return await get_incident(incident_id)

async def archive_incident(incident_id: str) -> dict:
    return await update_status(incident_id, "ARCHIVED")

async def add_note(incident_id: str, content: str, author: str, internal_only: bool = True) -> dict:
    db = await get_db()
    now_iso = datetime.datetime.utcnow().isoformat()
    
    note = {
        "note_id": str(uuid.uuid4()),
        "incident_id": incident_id,
        "author": author,
        "timestamp": now_iso,
        "content": content,
        "internal_only": internal_only
    }
    
    await db.incident_notes.insert_one(note)
    del note["_id"]
    
    # Update incident updated_at
    await db.incidents.update_one(
        {"incident_id": incident_id},
        {"$set": {"updated_at": now_iso}}
    )
    
    await audit.log_event(
        actor_username=author,
        action="NOTE_ADDED",
        resource_type="INCIDENT",
        resource_id=incident_id,
        incident_id=incident_id,
        description=f"Added internal note to incident"
    )
    
    return note

async def get_incident_notes(incident_id: str) -> List[dict]:
    db = await get_db()
    cursor = db.incident_notes.find({"incident_id": incident_id}, {"_id": 0}).sort("timestamp", 1)
    return await cursor.to_list(length=100)
