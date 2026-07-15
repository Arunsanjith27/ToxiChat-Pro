import requests
from auth import create_token
import os

token = create_token("admin", is_admin=True)
headers = {"Authorization": f"Bearer {token}"}
base_url = "http://localhost:8001"

print("--- TESTING IMAGE ANALYZE ---")
# Create a dummy image
with open("dummy.png", "wb") as f:
    f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82")

with open("dummy.png", "rb") as f:
    res = requests.post(f"{base_url}/api/image/analyze", headers=headers, files={"file": ("dummy.png", f, "image/png")})
    print(f"Status: {res.status_code}")
    print(f"Response: {res.json()}")
os.remove("dummy.png")

print("\n--- TESTING AUDIO ANALYZE ---")
with open("dummy.mp3", "wb") as f:
    f.write(b"ID3\x03\x00\x00\x00\x00\x00\x00")

with open("dummy.mp3", "rb") as f:
    res = requests.post(f"{base_url}/api/audio/analyze", headers=headers, files={"file": ("dummy.mp3", f, "audio/mpeg")})
    print(f"Status: {res.status_code}")
    print(f"Response: {res.json()}")
os.remove("dummy.mp3")


