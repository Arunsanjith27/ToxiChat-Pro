import os
import time
import difflib
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Winner model from benchmark
MODEL_NAME = "s-nlp/t5-paranmt-detox"
LOCAL_MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "rewrite-model")

# Global variables for caching model in memory
_tokenizer = None
_model = None
_is_ready = False

def load_model():
    """
    Downloads the model to local disk on first startup, then loads it fully offline.
    """
    global _tokenizer, _model, _is_ready
    
    if _is_ready:
        return
        
    print(f"[AI] Loading Rewrite model ({MODEL_NAME})...")
    try:
        if not os.path.exists(LOCAL_MODEL_PATH):
            print("[AI] Downloading Rewrite model for offline use (this may take a minute)...")
            os.makedirs(LOCAL_MODEL_PATH, exist_ok=True)
            _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
            _model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
            _tokenizer.save_pretrained(LOCAL_MODEL_PATH)
            _model.save_pretrained(LOCAL_MODEL_PATH)
            print("[OK] Rewrite model downloaded and saved locally")
        else:
            _tokenizer = AutoTokenizer.from_pretrained(LOCAL_MODEL_PATH, local_files_only=True)
            _model = AutoModelForSeq2SeqLM.from_pretrained(LOCAL_MODEL_PATH, local_files_only=True)
            print("[OK] Rewrite model loaded from local directory")
            
        _is_ready = True
    except Exception as e:
        print(f"[ERROR] Failed to load Rewrite model: {e}")
        _is_ready = False

def check_meaning_preservation(original: str, rewrite: str) -> float:
    """A heuristic check for meaning preservation."""
    return difflib.SequenceMatcher(None, original.lower(), rewrite.lower()).ratio()

def rewrite_message(message: str, analysis: dict) -> dict:
    """
    Generates a rewrite and validates it against the Toxicity model.
    Only returns a successful rewrite if toxicity is reduced and meaning is preserved.
    """
    if not _is_ready or not _tokenizer or not _model:
        load_model()
        
    start_time = time.time()
    result = {
        "rewritten_text": None,
        "model_used": MODEL_NAME,
        "processing_time_ms": 0,
        "status": "failed",
        "reason": "Model not loaded"
    }
    
    if not _is_ready:
        return result

    import ml_service # Imported here to avoid circular imports during startup if any
    
    # Generate rewrite
    try:
        inputs = _tokenizer(message, return_tensors="pt", max_length=128, truncation=True)
        outputs = _model.generate(**inputs, max_length=128, num_beams=4, early_stopping=True)
        candidate_text = _tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
    except Exception as e:
        print(f"[ERROR] Rewrite generation failed: {e}")
        result["reason"] = f"Generation error: {e}"
        result["processing_time_ms"] = int((time.time() - start_time) * 1000)
        return result
        
    # Validating the generated rewrite
    orig_tox_score = analysis.get("score", 1.0)
    
    new_analysis = ml_service.predict_toxicity(candidate_text)
    new_tox_score = new_analysis.get("score", 1.0)
    
    # 1. Check Toxicity Reduction
    if new_tox_score >= orig_tox_score:
        result["reason"] = "Toxicity not reduced"
        result["processing_time_ms"] = int((time.time() - start_time) * 1000)
        return result
        
    # 2. Check Meaning Preservation (heuristic threshold: at least 0.15 for short paraphrases)
    meaning_score = check_meaning_preservation(message, candidate_text)
    if meaning_score < 0.15:
        result["reason"] = "Meaning lost"
        result["processing_time_ms"] = int((time.time() - start_time) * 1000)
        return result

    # Accept Rewrite
    result["rewritten_text"] = candidate_text
    result["status"] = "success"
    result["reason"] = "Rewrite accepted"
    result["processing_time_ms"] = int((time.time() - start_time) * 1000)
    
    # Clean up output to exactly match user's requested schema:
    # "Return only: rewritten_text, model_used, processing_time_ms"
    # We will strip out 'status' and 'reason' for the final return if it's successful, 
    # but returning them as None or stripping is fine. We will strictly follow the signature.
    
    return {
        "rewritten_text": candidate_text,
        "model_used": MODEL_NAME,
        "processing_time_ms": result["processing_time_ms"]
    }
