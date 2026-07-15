# MongoDB Conversation Lookup Report

## Root Cause Analysis
During the stabilization of the AI Evidence Pipeline, it was identified that the `POST /api/conversation/summary` and `POST /api/admin/copilot` endpoints frequently returned 0 messages, stating *"There are no messages in this conversation context."*

**The Issue:**
Both endpoints fetch conversation context from MongoDB via `db.messages.find(...)`. The incoming payload for these endpoints contains a `conversation_id` string formatted as `user1_user2`.
To determine the `sender` and `receiver` for the query, the backend was executing a naive split:
```python
if "_" in conversation_id:
    u1, u2 = conversation_id.split("_", 1)
```
This naive splitting logic explicitly fails when either the sender or receiver's username itself contains an underscore (e.g., `admin_db_123` interacting with `test_user`).
In such a case, `admin_db_123_test_user` is incorrectly split on the **first** underscore, resulting in `u1 = admin` and `u2 = db_123_test_user`. Because there are no messages matching these fractured usernames, the query returns an empty cursor.

Furthermore, any group chat name containing an underscore (e.g., `my_awesome_group`) was erroneously being parsed as a Direct Message between `my` and `awesome_group`, completely ignoring the `is_group` context.

## The Fix
To completely bypass the limitations of string splitting and securely support any username or group name containing underscores, the query was refactored using MongoDB's `$expr` and `$concat` aggregation operators.

**Repaired Query Logic:**
```python
query = {
    "$or": [
        {
            "is_group": False,
            "$expr": {
                "$or": [
                    {"$eq": [{"$concat": ["$sender", "_", "$receiver"]}, conversation_id]},
                    {"$eq": [{"$concat": ["$receiver", "_", "$sender"]}, conversation_id]}
                ]
            }
        },
        {
            "is_group": True,
            "receiver": conversation_id
        }
    ]
}
```

**Why this preserves backward compatibility:**
1. **Frontend Compatibility:** The React UI (`ConversationPredictionCard`, `ConversationSummaryPanel`, and `ModeratorCopilotPanel`) continues to pass the unified `conversationId` exactly as it did before. No frontend changes were required.
2. **Schema Compatibility:** No changes were made to the MongoDB schema. It continues to natively support `sender`, `receiver`, and `is_group`.
3. **Accuracy:** The backend dynamically reconstructs the `conversationId` natively within the database engine during execution, perfectly matching any number of underscores in either user's name or the group's name. 

The `ai/manager.py` endpoints have been repaired and all debug logs have been successfully removed.
