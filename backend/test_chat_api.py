import asyncio
import websockets
import json
import requests
import pymongo
from contextlib import suppress

MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "toxichat_test"

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

async def test_chat():
    token1 = setup_user("chat_user1", "Chat User One")
    token2 = setup_user("chat_user2", "Chat User Two")

    print("Tokens retrieved.")

    async with websockets.connect(f"ws://localhost:8000/ws/{token1}") as ws1:
        # Wait for users_list
        u1_init = await ws1.recv()
        print("User 1 Connected.")
        
        async with websockets.connect(f"ws://localhost:8000/ws/{token2}") as ws2:
            u2_init = await ws2.recv()
            print("User 2 Connected.")
            
            # User 1 should receive presence_online for user 2
            presence_u2 = json.loads(await ws1.recv())
            # Skip system broadcast
            if presence_u2.get("type") == "system":
                presence_u2 = json.loads(await ws1.recv())
            assert presence_u2.get("type") == "presence_online"
            assert presence_u2.get("username") == "chat_user2"
            print("Presence Verified.")

            # Test Typing Indicator
            await ws1.send(json.dumps({"type": "typing_start", "receiver": "chat_user2"}))
            typing_event = json.loads(await ws2.recv())
            assert typing_event.get("type") == "typing_start"
            assert typing_event.get("sender") == "chat_user1"
            print("Typing Indicator Verified.")

            # Test Messaging
            test_text = "Hello, this is a test message!"
            await ws1.send(json.dumps({
                "type": "message",
                "receiver": "chat_user2",
                "text": test_text
            }))
            
            # User 1 receives echo back of the message sent
            msg_echo = json.loads(await ws1.recv())
            assert msg_echo.get("type") == "message"
            assert msg_echo.get("text") == test_text
            msg_id = msg_echo.get("id")

            # User 1 receives delivered receipt (since user 2 is online)
            receipt = json.loads(await ws1.recv())
            assert receipt.get("type") == "status_update"
            assert receipt.get("status") == "delivered"
            print("Message Sent and Read Receipt Received.")

            # User 2 receives the message
            msg_recv = json.loads(await ws2.recv())
            assert msg_recv.get("type") == "message"
            assert msg_recv.get("text") == test_text
            assert msg_recv.get("status") == "delivered"
            print("Message Received correctly by User 2.")
            
            # Verify DB
            db_msg = db.messages.find_one({"id": msg_id})
            assert db_msg is not None
            assert db_msg["text"] == test_text
            assert db_msg["status"] == "delivered"
            print("Database entry verified.")
            
            print("SUCCESS! Real-Time Chat is fully functional.")

if __name__ == "__main__":
    asyncio.run(test_chat())
