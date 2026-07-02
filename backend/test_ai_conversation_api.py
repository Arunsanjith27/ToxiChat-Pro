import requests
import json
import time

def setup_user(username, display_name):
    try:
        requests.post("http://localhost:8000/api/register", json={
            "username": username,
            "password": "TestPass123!",
            "display_name": display_name
        })
    except:
        pass
    
    resp = requests.post("http://localhost:8000/api/login", json={
        "username": username,
        "password": "TestPass123!"
    })
    return resp.json().get("access_token")

def insert_conversation_messages():
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017/")
    db = client["toxichat_test"]
    db.messages.delete_many({"sender": "convuser1"})
    db.messages.delete_many({"sender": "convuser2"})
    
    # Simulate a conversation
    messages = [
        {"sender": "convuser1", "receiver": "convuser2", "text": "Hello, how are you?", "timestamp": "2026-07-02T10:00:00Z"},
        {"sender": "convuser2", "receiver": "convuser1", "text": "I'm good. Did you see what happened today?", "timestamp": "2026-07-02T10:01:00Z"},
        {"sender": "convuser1", "receiver": "convuser2", "text": "No, what happened?", "timestamp": "2026-07-02T10:02:00Z"},
        {"sender": "convuser2", "receiver": "convuser1", "text": "Someone stole my car. I will kill whoever did this!", "timestamp": "2026-07-02T10:03:00Z"},
        {"sender": "convuser1", "receiver": "convuser2", "text": "Whoa, calm down, let's call the police.", "timestamp": "2026-07-02T10:04:00Z"}
    ]
    
    for m in messages:
        m["status"] = "delivered"
        m["is_group"] = False
        m["embedding"] = []
    
    db.messages.insert_many(messages)

def test_conversation_ai():
    print("Setting up test data...")
    token = setup_user("convuser1", "User 1")
    setup_user("convuser2", "User 2")
    insert_conversation_messages()
    
    headers = {"Authorization": f"Bearer {token}"}
    partner = "convuser2"
    
    print("\nTesting /api/conversation/health/{partner}...")
    res = requests.get(f"http://localhost:8000/api/conversation/health/{partner}", headers=headers)
    print("Health Status:", res.status_code)
    data = res.json()
    print("Health Response:", json.dumps(data, indent=2))
    assert res.status_code == 200, "Health failed"
    
    print("\nTesting /api/analytics/conversation/{partner}...")
    res = requests.get(f"http://localhost:8000/api/analytics/conversation/{partner}", headers=headers)
    print("Analytics Status:", res.status_code)
    data = res.json()
    print("Analytics Response:", json.dumps(data, indent=2))
    assert res.status_code == 200, "Analytics failed"
    
    # The endpoints /api/conversation/summary, /api/conversation/analytics/{id}, 
    # /api/conversation/prediction/{id} expect a `conversation_id`.
    # Let's assume conversation_id is "convuser1_convuser2" or similar.
    # Actually, let's look at what `analyze_conversation_orchestrator` expects.
    # It probably looks up messages for that conversation.
    conversation_id = f"convuser1_{partner}"
    
    print("\nTesting /api/conversation/summary...")
    res = requests.post("http://localhost:8000/api/conversation/summary", json={
        "conversation_id": conversation_id,
        "summary_type": "moderator"
    }, headers=headers)
    print("Summary Status:", res.status_code)
    data = res.json()
    print("Summary Response:", json.dumps(data, indent=2))
    assert res.status_code == 200, "Summary failed"
    
    print("\nTesting /api/conversation/analytics/{conversation_id}...")
    res = requests.get(f"http://localhost:8000/api/conversation/analytics/{conversation_id}", headers=headers)
    print("Analytics ID Status:", res.status_code)
    data = res.json()
    print("Analytics ID Response:", json.dumps(data, indent=2))
    assert res.status_code == 200, "Analytics ID failed"
    
    print("\nTesting /api/conversation/prediction/{conversation_id}...")
    res = requests.get(f"http://localhost:8000/api/conversation/prediction/{conversation_id}", headers=headers)
    print("Prediction Status:", res.status_code)
    data = res.json()
    print("Prediction Response:", json.dumps(data, indent=2))
    assert res.status_code == 200, "Prediction failed"
    
    print("\nSUCCESS! Conversation AI module verified.")

if __name__ == "__main__":
    test_conversation_ai()
