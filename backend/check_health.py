import requests
import json

res = requests.post("http://localhost:8000/api/login", json={"username": "ai_test_user", "password": "password123"})
if res.status_code != 200:
    print("Login failed:", res.text)
else:
    token = res.json()["access_token"]
    health = requests.get("http://localhost:8000/api/ai/health", headers={"Authorization": f"Bearer {token}"})
    print(json.dumps(health.json(), indent=2))
