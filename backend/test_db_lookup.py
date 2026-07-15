import requests
from pymongo import MongoClient

# 1. Register test user
import uuid
uid = str(uuid.uuid4())[:8]
uname = f'admin_db_{uid}'
print('Registering', uname)
requests.post('http://localhost:8000/api/register', json={
    'username': uname, 'password': 'TestPass123!', 'display_name': 'Admin DB Test'
})

# 2. Promote to admin
client = MongoClient('mongodb://localhost:27017/')
db = client['toxichat_test'] 
client['toxichat'].users.update_one({'username': uname}, {'$set': {'role': 'admin'}})
client['toxichat_test'].users.update_one({'username': uname}, {'$set': {'role': 'admin'}})

# 3. Login
token = requests.post('http://localhost:8000/api/login', json={
    'username': uname, 'password': 'TestPass123!'
}).json().get('access_token')

headers = {'Authorization': f'Bearer {token}'}

# 4. Insert messages into MongoDB
messages = [
    {'sender': uname, 'receiver': 'test_user2', 'text': 'Hello there', 'is_group': False},
    {'sender': 'test_user2', 'receiver': uname, 'text': 'Hi admin', 'is_group': False}
]
client['toxichat'].messages.insert_many(messages)
client['toxichat_test'].messages.insert_many(messages)

# 5. Test Copilot
print('=== Test Copilot ===')
res = requests.post('http://localhost:8000/api/admin/copilot', headers=headers, json={
    'conversation_id': f'{uname}_test_user2', 'question': 'What happened?'
})
print(res.json())

# 6. Test Summary
print('=== Test Summary ===')
res = requests.post('http://localhost:8000/api/conversation/summary', headers=headers, json={
    'conversation_id': f'{uname}_test_user2', 'summary_type': 'moderator'
})
print(res.json())
