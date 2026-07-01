import os
import warnings

# Suppress Hugging Face warnings if possible
warnings.filterwarnings("ignore")

# Centralized AI Models directory
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
EMOTION_MODEL_DIR = os.path.join(MODEL_DIR, "emotion-roberta")

_emotion_pipeline = None

def load_model():
    global _emotion_pipeline
    if _emotion_pipeline is not None:
        return

    print("[AI] Loading Emotion model...")
    try:
        from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

        if not os.path.exists(EMOTION_MODEL_DIR):
            print("[AI] Downloading emotion model for offline use (this may take a minute)...")
            model_name = "j-hartmann/emotion-english-distilroberta-base"
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSequenceClassification.from_pretrained(model_name)
            
            os.makedirs(EMOTION_MODEL_DIR, exist_ok=True)
            tokenizer.save_pretrained(EMOTION_MODEL_DIR)
            model.save_pretrained(EMOTION_MODEL_DIR)
            print("[OK] Emotion model downloaded and saved locally")

        _emotion_pipeline = pipeline(
            "text-classification",
            model=EMOTION_MODEL_DIR,
            tokenizer=EMOTION_MODEL_DIR,
            top_k=None,
            device=-1,
        )
        print("[OK] Emotion model loaded from local directory")
    except Exception as e:
        print(f"[WARN] Emotion model unavailable: {e}")
        _emotion_pipeline = None

def predict_emotion(text: str) -> dict:
    """
    Returns the predicted emotion label, confidence, and score.
    Returns neutral if text is empty or model unavailable.
    """
    if not text or not text.strip():
        return {"label": "neutral", "confidence": 0.0, "score": 0.0}

    if _emotion_pipeline is None:
        load_model()
    
    if _emotion_pipeline is None:
        return {"label": "neutral", "confidence": 0.0, "score": 0.0}

    try:
        results = _emotion_pipeline(text, truncation=True, max_length=512)
        if isinstance(results, list) and isinstance(results[0], list):
            results = results[0]
        
        # results looks like: [{'label': 'joy', 'score': 0.9}, ...]
        best = max(results, key=lambda x: x["score"])
        return {
            "label": best["label"].lower(),
            "confidence": round(best["score"], 4),
            "score": round(best["score"], 4)
        }
    except Exception as e:
        print(f"[WARN] Emotion prediction error: {e}")
        return {"label": "neutral", "confidence": 0.0, "score": 0.0}

# Initialize on import
load_model()
