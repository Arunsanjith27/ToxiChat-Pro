import requests
from auth import create_token
import asyncio
from database import get_db, _use_memory

async def main():
    token = create_token("admin", is_admin=True)
    headers = {"Authorization": f"Bearer {token}"}
    base_url = "http://localhost:8001"

    print("--- FETCHING CONVERSATIONS ---")
    res_hr = requests.get(f"{base_url}/api/admin/analytics/high-risk", headers=headers)
    hr = res_hr.json()
    if not hr:
        print("No high risk conversations found")
        return
    conv = hr[0]
    
    target_user = conv.get("user1") if conv.get("user1") != "admin" else conv.get("user2")
    if conv.get("type") == "group":
        target_user = conv.get("group_name")
        conv_id = conv.get("group_name")
    else:
        conv_id = f"{conv['user1']}_{conv['user2']}"

    print("--- CREATING INCIDENT ---")
    res = requests.post(
        f"{base_url}/api/incidents",
        headers=headers,
        json={
            "type": "TOXICITY",
            "target_user": target_user,
            "conversation_id": conv_id,
            "priority": "HIGH",
            "description": "Test incident"
        }
    )
    print(res.json())
    inc_id = res.json().get("incident_id")
    if not inc_id:
        print("Failed to create incident")
        return

    print("--- TESTING REPORT GENERATION ---")
    res = requests.post(f"{base_url}/api/reports/generate", headers=headers, json={"incident_id": inc_id})
    print(f"Status: {res.status_code}")
    if res.status_code == 200:
        report = res.json()
        print(f"Response: {report}")
        report_id = report["report_id"]
        
        print("\n--- TESTING REPORT DOWNLOAD ---")
        res_dl = requests.get(f"{base_url}/api/reports/download/{report_id}?format=pdf", headers=headers)
        print(f"Status: {res_dl.status_code}")
        print(f"Content Type: {res_dl.headers.get('Content-Type')}")
        print(f"Length: {len(res_dl.content)}")
    else:
        print(f"Error: {res.json()}")

if __name__ == "__main__":
    asyncio.run(main())
