import requests
from auth import create_token
import asyncio

token = create_token("admin", is_admin=True)

res = requests.get("http://localhost:8000/api/admin/analytics/high-risk", headers={"Authorization": f"Bearer {token}"})
print(res.status_code)
print(res.json())

res2 = requests.get("http://localhost:8000/api/dashboard/stats", headers={"Authorization": f"Bearer {token}"})
print(res2.status_code)
print(res2.json())
