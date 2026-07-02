import asyncio
import json
import requests
import pymongo

MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "toxichat"

client = pymongo.MongoClient(MONGO_URL)
db = client[DB_NAME]

def setup_user(username, display_name):
    db.users.delete_many({"username": username})
    requests.post("http://localhost:8000/api/register", json={
        "username": username,
        "password": "TestPass123!",
        "display_name": display_name
    })
    resp = requests.post("http://localhost:8000/api/login", json={
        "username": username,
        "password": "TestPass123!"
    })
    return resp.json().get("access_token")

def test_text_ai():
    token = setup_user("ai_test_user", "AI Test User")
    headers = {"Authorization": f"Bearer {token}"}
    
    print("Testing /api/predict (Toxicity, Emotion, PII, Explainability)...")
    res = requests.post("http://localhost:8000/api/predict", json={"text": "I will kill you!"}, headers=headers)
    print("Predict Status:", res.status_code)
    predict_data = res.json()
    print("Predict Response:", json.dumps(predict_data, indent=2))
    assert predict_data["is_flagged"] == True, "Failed to flag toxic message"
    
    print("\nTesting /api/predict/escalation (Risk Engine)...")
    res = requests.post("http://localhost:8000/api/predict/escalation", json={"text": "You are stupid.", "partner": "some_user"}, headers=headers)
    print("Escalation Status:", res.status_code)
    esc_data = res.json()
    print("Escalation Response:", json.dumps(esc_data, indent=2))
    assert "escalation" in esc_data, "Missing escalation data"
    
    print("\nTesting /api/rewrite...")
    res = requests.post("http://localhost:8000/api/rewrite", json={"text": "You are stupid."}, headers=headers)
    print("Rewrite Status:", res.status_code)
    rewrite_data = res.json()
    print("Rewrite Response:", json.dumps(rewrite_data, indent=2))
    assert "rewritten" in rewrite_data, "Missing rewritten text"
    
    print("\nTesting /api/search...")
    # Get embedding for the test message
    test_text = "This is a very unique search query text for testing."
    predict_res = requests.post("http://localhost:8000/api/predict", json={"text": test_text}, headers=headers)
    
    import sys, os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from ai import embedding_service
    embedding = embedding_service.generate_embedding(test_text)
    
    # First send a message to search for
    db.messages.insert_one({
        "sender": "ai_test_user",
        "receiver": "some_user",
        "text": test_text,
        "status": "delivered",
        "is_group": False,
        "embedding": embedding,
        "timestamp": "2026-01-01T00:00:00Z"
    })
    res = requests.get("http://localhost:8000/api/search?q=unique search query", headers=headers)
    print("Search Status:", res.status_code)
    search_data = res.json()
    print("Search Response Size:", len(search_data))
    
    if len(search_data) == 0:
        health_res = requests.get("http://localhost:8000/api/ai/health", headers=headers)
        print("AI Health Response:")
        print(json.dumps(health_res.json(), indent=2))
        
    assert len(search_data) > 0, "Search failed to find message"
    assert "unique search query" in search_data[0]["text"], "Incorrect search result"
    
    print("\nSUCCESS! Text AI module verified.")

if __name__ == "__main__":
    test_text_ai()
