import os
import warnings

warnings.filterwarnings("ignore")

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
PII_MODEL_DIR = os.path.join(MODEL_DIR, "gliner-pii")

_pii_model = None

PII_LABELS = [
    "Phone Number", 
    "Email", 
    "Aadhaar Number", 
    "PAN Number", 
    "Credit Card", 
    "Bank Account", 
    "UPI ID", 
    "Passport Number", 
    "Driving License", 
    "Address"
]

def load_model():
    global _pii_model
    if _pii_model is not None:
        return

    print("[AI] Loading PII model...")
    try:
        from gliner import GLiNER

        if not os.path.exists(PII_MODEL_DIR):
            print("[AI] Downloading GLiNER PII model for offline use (this may take a minute)...")
            model = GLiNER.from_pretrained("knowledgator/gliner-pii-base-v1.0")
            os.makedirs(PII_MODEL_DIR, exist_ok=True)
            model.save_pretrained(PII_MODEL_DIR)
            print("[OK] PII model downloaded and saved locally")

        # Load from local directory to ensure fully offline inference
        _pii_model = GLiNER.from_pretrained(PII_MODEL_DIR, local_files_only=True)
        print("[OK] PII model loaded from local directory")
    except Exception as e:
        print(f"[WARN] PII model unavailable: {e}")
        _pii_model = None

def detect_pii(text: str) -> dict:
    """
    Returns a dict with 'contains_pii' (bool) and 'entities' (list of dicts).
    """
    if not text or not text.strip():
        return {"contains_pii": False, "entities": []}

    if _pii_model is None:
        load_model()
    
    if _pii_model is None:
        return {"contains_pii": False, "entities": []}

    try:
        # GLiNER predict_entities returns list of dicts: 
        # [{'text': '...', 'label': '...', 'score': 0.9}, ...]
        entities_raw = _pii_model.predict_entities(text, PII_LABELS)
        
        entities = []
        for ent in entities_raw:
            # We filter for a threshold if necessary, GLiNER usually outputs confident predictions
            if ent.get("score", 1.0) > 0.5:
                entities.append({
                    "type": ent["label"],
                    "value": ent["text"],
                    "confidence": round(ent.get("score", 1.0), 4)
                })

        return {
            "contains_pii": len(entities) > 0,
            "entities": entities
        }
    except Exception as e:
        print(f"[WARN] PII prediction error: {e}")
        return {"contains_pii": False, "entities": []}

# Initialize on import
load_model()
