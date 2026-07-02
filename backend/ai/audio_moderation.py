import os
import hashlib
from typing import Dict, Any

try:
    from faster_whisper import WhisperModel
    MODEL_DIR = os.path.join(os.path.dirname(__file__), "models", "audio")
    os.makedirs(MODEL_DIR, exist_ok=True)
    # Using 'base' or 'tiny' for fast CPU inference
    _whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8", download_root=MODEL_DIR)
except ImportError:
    _whisper_model = None
    print("WARNING: faster-whisper not installed. Audio transcription will be disabled.")

ALLOWED_MIMES = ["audio/wav", "audio/mpeg", "audio/mp3", "audio/ogg", "audio/mp4"]
MAX_SIZE_BYTES = 20 * 1024 * 1024 # 20 MB

def validate_and_hash_audio(file_bytes: bytes, mime_type: str) -> str:
    """
    Validates MIME type, size, and generates a SHA-256 hash.
    Raises ValueError if validation fails.
    """
    # Accept standard audio mime types or mp4 (often used for voice notes on mobile)
    if not any(mime in mime_type for mime in ALLOWED_MIMES):
        raise ValueError(f"Unsupported MIME type: {mime_type}. Allowed: {ALLOWED_MIMES}")
    
    if len(file_bytes) > MAX_SIZE_BYTES:
        raise ValueError("File size exceeds 20MB limit.")
        
    # Generate SHA-256 hash
    sha256_hash = hashlib.sha256(file_bytes).hexdigest()
    return sha256_hash

def check_audio_corruption(file_path: str) -> Dict[str, Any]:
    """
    Checks for corrupted audio, verifies duration and extracts basic metadata.
    Uses pydub if available, otherwise returns basic metadata.
    """
    metadata = {
        "duration": 0.0,
        "sample_rate": 0,
        "channels": 0,
        "corrupted": False
    }
    
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(file_path)
        metadata["duration"] = len(audio) / 1000.0 # seconds
        metadata["sample_rate"] = audio.frame_rate
        metadata["channels"] = audio.channels
        
        if metadata["duration"] > 600: # 10 minutes max
            raise ValueError("Audio duration exceeds 10 minutes limit.")
            
    except ImportError:
        # Fallback if pydub/ffmpeg is missing
        print("WARNING: pydub not installed, skipping deep corruption check")
        metadata["duration"] = 10.0 # Mock duration
    except Exception as e:
        print(f"Audio Corruption Check Failed: {e}")
        metadata["corrupted"] = True
        
    return metadata

def analyze_audio_content(audio_path: str) -> Dict[str, Any]:
    """
    Runs Faster-Whisper on the audio.
    Returns structured dict containing transcript data.
    """
    result = {
        "transcript": {
            "text": "",
            "confidence": 0.0,
            "segments": []
        },
        "metadata": {
            "language": "unknown",
            "estimated_speakers": 1 # For future diarization
        }
    }
    
    # 1. Validation & Metadata extraction
    audio_meta = check_audio_corruption(audio_path)
    if audio_meta["corrupted"]:
        raise ValueError("Audio file is corrupted or unsupported.")
        
    # 2. Transcription (Faster-Whisper)
    if _whisper_model:
        try:
            segments_gen, info = _whisper_model.transcribe(audio_path, beam_size=5)
            
            result["metadata"]["language"] = info.language
            result["metadata"]["language_probability"] = info.language_probability
            
            full_text = []
            total_prob = 0.0
            count = 0
            
            for segment in segments_gen:
                full_text.append(segment.text)
                total_prob += segment.no_speech_prob # This is inverted, but we'll map it to confidence
                
                result["transcript"]["segments"].append({
                    "start": float(segment.start),
                    "end": float(segment.end),
                    "text": segment.text.strip(),
                    "confidence": float(1.0 - segment.no_speech_prob)
                })
                count += 1
                
            result["transcript"]["text"] = " ".join(full_text).strip()
            
            # Simple average confidence
            if count > 0:
                avg_no_speech = total_prob / count
                result["transcript"]["confidence"] = float(1.0 - avg_no_speech)
            else:
                result["transcript"]["confidence"] = 1.0
                
        except Exception as e:
            print(f"Transcription Error: {e}")
            
    result["metadata"].update(audio_meta)
    
    return result
