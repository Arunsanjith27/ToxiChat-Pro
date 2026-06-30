import os
import warnings

_toxicity_pipeline = None
_emotion_pipeline = None
_toxicity_ready = False
_emotion_ready = False

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models")


def load_all_models():
    global _toxicity_pipeline, _toxicity_ready
    global _emotion_pipeline, _emotion_ready

    print("[AI] Loading models...")

    try:
        from transformers import pipeline as hf_pipeline, AutoTokenizer, AutoModelForSequenceClassification
        
        # 1. Try to load new RoBERTa model
        roberta_dir = os.path.join(MODEL_DIR, "unbiased-toxic-roberta")
        if not os.path.exists(roberta_dir):
            print("[AI] Downloading unitary/unbiased-toxic-roberta for offline use (this may take a minute)...")
            tokenizer = AutoTokenizer.from_pretrained("unitary/unbiased-toxic-roberta")
            model = AutoModelForSequenceClassification.from_pretrained("unitary/unbiased-toxic-roberta")
            tokenizer.save_pretrained(roberta_dir)
            model.save_pretrained(roberta_dir)
            print("[OK] unbiased-toxic-roberta downloaded and saved locally")

        _toxicity_pipeline = hf_pipeline(
            "text-classification",
            model=roberta_dir,
            tokenizer=roberta_dir,
            top_k=None,
            device=-1,
        )
        _toxicity_ready = True
        print("[OK] unbiased-toxic-roberta loaded from local directory")
        
    except Exception as e_roberta:
        print(f"[WARN] unbiased-toxic-roberta unavailable: {e_roberta}")
        
        # 2. Fallback to old toxic-bert model
        try:
            print("[AI] Attempting to load legacy toxic-bert fallback...")
            local_model_dir = os.path.join(MODEL_DIR, "toxic-bert")
            if os.path.exists(local_model_dir):
                _toxicity_pipeline = hf_pipeline(
                    "text-classification",
                    model=local_model_dir,
                    tokenizer=local_model_dir,
                    top_k=None,
                    device=-1,
                )
                _toxicity_ready = True
                print("[OK] legacy toxic-bert fallback loaded")
            else:
                raise Exception("Legacy toxic-bert directory not found")
        except Exception as e_bert:
            print(f"[WARN] fallback toxic-bert unavailable: {e_bert}")
            _toxicity_ready = False
    try:
        from transformers import pipeline as hf_pipeline
        _emotion_pipeline = hf_pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            top_k=None,
            device=-1,
        )
        _emotion_ready = True
        print("[OK] emotion-distilroberta loaded")
    except Exception as e:
        print(f"[WARN] emotion model unavailable: {e}")
        _emotion_ready = False

    active = []
    if _toxicity_ready:
        active.append("toxic-bert")
    if _emotion_ready:
        active.append("emotion-distilroberta")
    print(f"[AI] Active models: {', '.join(active)}")


def get_toxicity_pipeline():
    return _toxicity_pipeline if _toxicity_ready else None


def get_emotion_pipeline():
    return _emotion_pipeline if _emotion_ready else None


def is_transformer_ready():
    return _toxicity_ready


def is_emotion_ready():
    return _emotion_ready


load_all_models()
