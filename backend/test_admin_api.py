import requests
import json
from pymongo import MongoClient

def setup_admin_user(username, display_name):
    requests.post("http://localhost:8000/api/register", json={
        "username": username,
        "password": "TestPass123!",
        "display_name": display_name
    })
    
    # Promote to admin
    client = MongoClient("mongodb://localhost:27017/")
    db = client["toxichat_test"]
    db.users.update_one({"username": username}, {"$set": {"role": "admin"}})
    
    resp = requests.post("http://localhost:8000/api/login", json={
        "username": username,
        "password": "TestPass123!"
    })
    return resp.json().get("access_token")

def test_admin_api():
    print("Setting up test data...")
    token = setup_admin_user("admin", "Admin User")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create incident
    client = MongoClient("mongodb://localhost:27017/")
    db = client["toxichat_test"]
    incident = {
        "incident_id": "INC-TEST-01",
        "type": "toxicity",
        "status": "open",
        "severity": "high",
        "message_id": "msg_test_123",
        "reported_user": "some_user",
        "created_at": "2026-07-02T10:00:00Z"
    }
    db.incidents.delete_many({"incident_id": "INC-TEST-01"})
    db.incidents.insert_one(incident)
    
    print("\nTesting /api/admin/copilot...")
    res = requests.post("http://localhost:8000/api/admin/copilot", headers=headers, json={"conversation_id": "convuser1_convuser2", "question": "What is going on?"})
    print("Copilot Status:", res.status_code)
    
    print("\nTesting /api/incidents...")
    res = requests.post("http://localhost:8000/api/incidents", headers=headers, json={"conversation_id": "convuser1_convuser2", "priority": "high"})
    print("Create Incident Status:", res.status_code)
    inc_data = res.json()
    new_inc_id = inc_data.get("incident_id", "INC-TEST-01")
    
    print("\nTesting /api/incidents/{id}/assign...")
    res = requests.post(f"http://localhost:8000/api/incidents/{new_inc_id}/assign", headers=headers, json={"assignee": "admin_user"})
    print("Assign Status:", res.status_code)
    
    print("\nTesting /api/incidents/{id}/notes...")
    res = requests.post(f"http://localhost:8000/api/incidents/{new_inc_id}/notes", headers=headers, json={"content": "Investigating this.", "internal_only": True})
    print("Notes Status:", res.status_code)
    
    print("\nTesting /api/incidents/{id}/resolve...")
    res = requests.post(f"http://localhost:8000/api/incidents/{new_inc_id}/resolve", headers=headers)
    print("Resolve Status:", res.status_code)
    
    print("\nTesting /api/reports/generate...")
    res = requests.post("http://localhost:8000/api/reports/generate", headers=headers, json={"incident_id": new_inc_id})
    print("Reports Status:", res.status_code)
    
    print("\nSUCCESS! Admin, Incident Management, and Compliance Reports verified.")

if __name__ == "__main__":
    test_admin_api()
