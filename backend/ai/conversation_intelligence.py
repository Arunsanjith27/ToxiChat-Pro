import os
import time
from typing import Dict, Any

from transformers import pipeline

from ai.context_builder import build_structured_context

# The winning model from the benchmark
WINNING_MODEL = "Falconsai/text_summarization"
MODEL_LOCAL_DIR = os.path.join(os.path.dirname(__file__), "models", "conversation-intelligence")

_tokenizer = None
_model = None

def _get_pipeline():
    global _tokenizer, _model
    if _tokenizer is not None and _model is not None:
        return _tokenizer, _model
        
    print(f"Loading Conversation Intelligence Model ({WINNING_MODEL})...")
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    
    if os.path.exists(MODEL_LOCAL_DIR) and os.listdir(MODEL_LOCAL_DIR):
        print(f"Loading from local cache: {MODEL_LOCAL_DIR}")
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_LOCAL_DIR)
        _model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_LOCAL_DIR)
    else:
        print(f"Downloading from Hugging Face: {WINNING_MODEL}")
        os.makedirs(MODEL_LOCAL_DIR, exist_ok=True)
        _tokenizer = AutoTokenizer.from_pretrained(WINNING_MODEL)
        _model = AutoModelForSeq2SeqLM.from_pretrained(WINNING_MODEL)
        _tokenizer.save_pretrained(MODEL_LOCAL_DIR)
        _model.save_pretrained(MODEL_LOCAL_DIR)
        print("Model cached locally for offline use.")
        
    return _tokenizer, _model

def generate_summary(conversation: list, analytics: dict, summary_type: str = "moderator") -> Dict[str, Any]:
    """
    Generates a high-quality abstractive summary of the conversation
    by summarizing a structured context built from AI metadata.
    """
    start_time = time.time()
    
    # 1. Build structured context (Do not summarize raw chat directly!)
    structured_context = build_structured_context(analytics, summary_type)
    
    # 2. Run offline NLP summarization
    tokenizer, model = _get_pipeline()
    
    try:
        inputs = tokenizer(structured_context, return_tensors="pt", max_length=512, truncation=True)
        outputs = model.generate(inputs.input_ids, max_length=150, min_length=20, do_sample=False)
        summary_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    except Exception as e:
        print(f"Error during summarization: {e}")
        summary_text = structured_context  # Fallback to the context string if inference fails
        
    gen_time_ms = int((time.time() - start_time) * 1000)
    
    return {
        "summary_text": summary_text,
        "model_used": WINNING_MODEL,
        "generation_time_ms": gen_time_ms,
        "conversation_health": analytics.get("conversation_health_score", 0),
        "risk_level": analytics.get("conversation_state", "UNKNOWN"),
        "dominant_emotion": _get_dominant_emotion(analytics),
        "recommendation": _generate_recommendation(analytics, summary_type)
    }

def _get_dominant_emotion(analytics: dict) -> str:
    emotions = analytics.get("emotion_distribution", {})
    if not emotions:
        return "Neutral"
    return max(emotions, key=emotions.get)

def _generate_recommendation(analytics: dict, summary_type: str) -> str:
    risk = analytics.get("average_risk_score", 0)
    if risk > 70:
        return "Immediate moderator intervention required."
    elif risk > 40:
        return "Monitor conversation for further escalation."
    else:
        return "No action required."
