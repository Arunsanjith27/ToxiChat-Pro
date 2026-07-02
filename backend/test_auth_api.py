import requests
import pymongo

MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "toxichat_test"

client = pymongo.MongoClient(MONGO_URL)
db = client[DB_NAME]
db.users.delete_many({"username": "auth_test_user"})

# 1. Register
print("Registering...")
resp = requests.post("http://localhost:8000/api/register", json={
    "username": "auth_test_user",
    "password": "TestPass123!",
    "display_name": "Test User Auth"
})
print("Register Status:", resp.status_code)
print("Register Response:", resp.text)

if resp.status_code == 200:
    token = resp.json().get("access_token")
    print("User in DB:", db.users.find_one({"username": "auth_test_user"}) is not None)
    
    # 2. /api/me
    print("Fetching /api/me...")
    resp = requests.get("http://localhost:8000/api/me", headers={"Authorization": f"Bearer {token}"})
    print("/api/me Status:", resp.status_code)
    print("/api/me Response:", resp.text)
    
    # 3. Login
    print("Logging in...")
    resp = requests.post("http://localhost:8000/api/login", json={
        "username": "auth_test_user",
        "password": "TestPass123!"
    })
    print("Login Status:", resp.status_code)
    print("Login Response:", resp.text)
