import os
import hashlib
from typing import Dict, Any

try:
    import easyocr
    _ocr_reader = easyocr.Reader(['en'], gpu=False)
except ImportError:
    _ocr_reader = None
    print("WARNING: easyocr not installed. OCR will be disabled.")

try:
    from nudenet import NudeDetector
    _nude_detector = NudeDetector()
except ImportError:
    _nude_detector = None
    print("WARNING: nudenet not installed. Vision NSFW will be disabled.")

ALLOWED_MIMES = ["image/jpeg", "image/png", "image/webp"]
MAX_SIZE_BYTES = 5 * 1024 * 1024 # 5 MB

def validate_and_hash_image(file_bytes: bytes, mime_type: str) -> str:
    """
    Validates MIME type, size, and generates a SHA-256 hash.
    Raises ValueError if validation fails.
    """
    if mime_type not in ALLOWED_MIMES:
        raise ValueError(f"Unsupported MIME type: {mime_type}. Allowed: {ALLOWED_MIMES}")
    
    if len(file_bytes) > MAX_SIZE_BYTES:
        raise ValueError("File size exceeds 5MB limit.")
        
    # Generate SHA-256 hash
    sha256_hash = hashlib.sha256(file_bytes).hexdigest()
    return sha256_hash

def analyze_image_content(image_path: str) -> Dict[str, Any]:
    """
    Runs OCR and Vision models on the image.
    Returns structured dict containing 'ocr' and 'vision' data.
    """
    result = {
        "ocr": {
            "contains_text": False,
            "text": "",
            "confidence": 0.0,
            "regions": []
        },
        "vision": {
            "nsfw_score": 0.0,
            "violence_score": 0.0
        }
    }
    
    # 1. OCR (EasyOCR)
    if _ocr_reader:
        try:
            ocr_results = _ocr_reader.readtext(image_path)
            if ocr_results:
                result["ocr"]["contains_text"] = True
                
                full_text = []
                avg_conf = 0.0
                
                for bbox, text, prob in ocr_results:
                    full_text.append(text)
                    avg_conf += prob
                    result["ocr"]["regions"].append({
                        "box": [[int(coord) for coord in point] for point in bbox],
                        "text": text,
                        "confidence": float(prob)
                    })
                    
                result["ocr"]["text"] = " ".join(full_text)
                result["ocr"]["confidence"] = float(avg_conf / len(ocr_results))
        except Exception as e:
            print(f"OCR Error: {e}")

    # 2. Vision (NudeNet)
    if _nude_detector:
        try:
            # NudeNet returns a list of dicts with 'class' and 'score'
            # Classes include 'EXPOSED_BELLY', 'EXPOSED_BUTTOCKS', 'EXPOSED_BREAST_F', 'EXPOSED_GENITALIA_F', etc.
            detections = _nude_detector.detect(image_path)
            max_nsfw_score = 0.0
            
            for det in detections:
                label = det.get('class', '')
                score = det.get('score', 0.0)
                if 'EXPOSED' in label and score > max_nsfw_score:
                    max_nsfw_score = float(score)
                    
            result["vision"]["nsfw_score"] = max_nsfw_score
            # We don't have violence out of the box with default NudeNet
            result["vision"]["violence_score"] = 0.0
            
        except Exception as e:
            print(f"Vision Error: {e}")
            
    return result
