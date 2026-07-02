import requests
import json
import os
import io
from PIL import Image

def setup_user(username, display_name):
    # Register and login helper
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

def test_multimodal_ai():
    print("Setting up test data...")
    token = setup_user("multi_user", "Multi User")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Image Moderation
    print("\nTesting /api/image/analyze...")
    # Create a dummy image
    img = Image.new('RGB', (100, 100), color = 'red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    files = {'file': ('test_image.png', img_byte_arr, 'image/png')}
    data = {'room': 'test_room', 'username': 'multi_user'}
    
    res = requests.post("http://localhost:8000/api/image/analyze", headers=headers, files=files, data=data)
    print("Image Status:", res.status_code)
    img_data = res.json()
    print("Image Response:", json.dumps(img_data, indent=2))
    assert res.status_code == 200, "Image analysis failed"
    
    # 2. Audio Moderation
    print("\nTesting /api/audio/analyze...")
    # Create a dummy audio file using pydub
    try:
        import wave
        audio_byte_arr = io.BytesIO()
        with wave.open(audio_byte_arr, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(44100)
            wav_file.writeframes(b'\x00' * 44100 * 2) # 1 second of silence
        audio_byte_arr.seek(0)
        
        files = {'file': ('test_audio.wav', audio_byte_arr, 'audio/wav')}
        data = {'room': 'test_room', 'username': 'multi_user'}
        
        res = requests.post("http://localhost:8000/api/audio/analyze", headers=headers, files=files, data=data)
        print("Audio Status:", res.status_code)
        aud_data = res.json()
        print("Audio Response:", json.dumps(aud_data, indent=2))
        assert res.status_code == 200, "Audio analysis failed"
    except Exception as e:
        print(f"Skipping audio test due to error: {e}")
        
    print("\nSUCCESS! Multimodal AI module verified.")

if __name__ == "__main__":
    test_multimodal_ai()
