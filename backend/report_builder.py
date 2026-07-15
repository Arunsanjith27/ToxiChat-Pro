import hashlib
import json
import datetime
from typing import Dict, Any

from database import get_db
import incidents
import audit

async def build_report_object(incident_id: str, generated_by: str) -> Dict[str, Any]:
    """
    Aggregates all existing platform intelligence into one immutable ReportObject.
    Does NOT rerun any AI inference.
    """
    db = await get_db()
    
    # 1. Fetch Incident Snapshot
    incident = await incidents.get_incident(incident_id)
    
    # 2. Fetch Conversation History (for snapshot)
    conversation_id = incident.get("conversation_id")
    messages = []
    if conversation_id:
        from database import get_messages_for_conversation
        participants = incident.get("metadata", {}).get("participants")
        is_group = incident.get("metadata", {}).get("is_group")
        messages = await get_messages_for_conversation(db, conversation_id, participants=participants, is_group=is_group, limit=100)
        
    # 3. Fetch Audit Trail for this incident
    audit_trail = await audit.get_incident_history(incident_id)
    
    # 4. Fetch Moderator Notes
    notes = await incidents.get_incident_notes(incident_id)
    
    # Assemble the core object
    now_iso = datetime.datetime.utcnow().isoformat()
    
    report_object = {
        "metadata": {
            "generated_date": now_iso,
            "generated_by": generated_by,
            "system_version": "1.0.0",
            "ai_pipeline_version": "2.1.0",
            "schema_version": "1.0",
            "report_type": "Incident Report"
        },
        "incident_overview": {
            "incident_id": incident_id,
            "status": incident.get("status"),
            "priority": incident.get("priority"),
            "assigned_moderator": incident.get("assigned_to"),
            "created_date": incident.get("created_at"),
            "resolved_date": incident.get("resolved_at"),
            "tags": incident.get("tags", [])
        },
        "analytics_snapshot": incident.get("analytics_snapshot", {}),
        "prediction_snapshot": incident.get("prediction_snapshot", {}),
        "copilot_snapshot": incident.get("copilot_snapshot", {}),
        "evidence": {
            "message_count": len(messages),
            "conversation_snapshot": messages
            # Image, Voice, OCR evidence would be fetched from messages metadata if they exist
        },
        "timeline": audit_trail,
        "moderator_notes": notes
    }
    
    # 5. Generate SHA-256 Hash
    # We must sort keys to ensure deterministic hashing
    report_json_str = json.dumps(report_object, sort_keys=True)
    report_hash = hashlib.sha256(report_json_str.encode('utf-8')).hexdigest()
    
    report_object["metadata"]["report_hash"] = report_hash
    
    return report_object
