import httpx
from PIL import Image
Image.new('RGB', (100, 100)).save("test.jpg")
files = {'file': ('test.jpg', open("test.jpg", "rb"), 'image/jpeg')}
r = httpx.post("http://127.0.0.1:8000/api/image/analyze", files=files)
print(r.status_code)
print(r.json())
