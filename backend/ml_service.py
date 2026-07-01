import re
import numpy as np
import ai_model

TOXICITY_THRESHOLD = 0.5

TOXIC_KEYWORDS = [
    'fuck', 'fucking', 'fucker', 'bitch', 'shit', 'piss', 'cunt', 'slut', 'whore',
    'dick', 'pussy', 'asshole', 'bastard', 'motherfucker',
    'idiot', 'stupid', 'dumb', 'moron', 'retard', 'trash', 'garbage', 'scum',
    'loser', 'worthless', 'ugly', 'disgusting', 'pathetic', 'shut up', 'get lost',
    'hate', 'kill', 'die', 'murder', 'suicide'
]

SAFE_WORDS = [
    'hello', 'hi', 'hey', 'bye', 'goodbye', 'father', 'mother', 'brother',
    'sister', 'family', 'friend', 'love', 'amazing', 'great', 'good',
    'thanks', 'thank', 'please', 'welcome', 'sorry', 'okay', 'ok', 'yes', 'no'
]

REWRITE_MAP = {
    "fuck": "heck", "fucking": "freaking", "shit": "crap", "bitch": "person",
    "asshole": "jerk", "bastard": "fool", "idiot": "person", "stupid": "silly",
    "dumb": "uninformed", "moron": "person", "retard": "person",
    "hate": "dislike", "kill": "stop", "die": "go away",
    "ugly": "not great", "disgusting": "unpleasant", "pathetic": "disappointing",
    "loser": "person", "worthless": "undervalued", "trash": "not great",
    "shut up": "please be quiet", "get lost": "please leave",
    "slut": "person", "whore": "person", "cunt": "person",
}

_hf_ready = ai_model.is_transformer_ready()
_ready = _hf_ready


def _score_to_label(score: float) -> str:
    if score >= 0.80:
        return "Severe"
    if score >= 0.50:
        return "Moderate"
    if score >= 0.20:
        return "Mild"
    return "Safe"


def _find_toxic_words(text: str) -> list:
    found = []
    text_lower = text.lower()
    for kw in TOXIC_KEYWORDS:
        if re.search(rf'\b{re.escape(kw)}\b', text_lower):
            for word in text.split():
                if re.search(rf'\b{re.escape(kw)}\b', word.lower()):
                    found.append(word)
    return list(set(found))


def _clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'http\S+|www\S+', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[^a-z\s]', ' ', text)
    return ' '.join(text.split())


def _predict_transformer(text: str) -> dict | None:
    pipe = ai_model.get_toxicity_pipeline()
    if pipe is None:
        return None
    try:
        # Use native tokenizer truncation to properly handle long sequences
        results = pipe(text, truncation=True, max_length=512)
        if isinstance(results, list) and isinstance(results[0], list):
            results = results[0]
        toxic_labels = ["toxic", "toxicity", "severe_toxicity", "identity_attack", "threat", "insult"]
        toxic_score = 0.0
        for r in results:
            if r["label"].lower() in toxic_labels:
                toxic_score = max(toxic_score, r["score"])
        return {"score": round(toxic_score, 4)}
    except Exception:
        return None


def _build_context_text(text: str, context: list) -> str:
    if not context:
        return text
    # Keep the most recent 3-5 messages intact. We use 4 here.
    recent = [m.get("text", "") if isinstance(m, dict) else str(m) for m in context[-4:]]
    combined = " ".join(recent) + " " + text
    return combined


def predict_toxicity(text: str) -> dict:
    if not text or not text.strip():
        return {"score": 0.0, "label": "Safe", "is_flagged": False, "toxic_words": []}

    text_lower = text.lower()
    words = text_lower.split()
    if len(words) <= 3 and any(re.search(rf'\b{re.escape(sw)}\b', text_lower) for sw in SAFE_WORDS):
        if not any(re.search(rf'\b{re.escape(kw)}\b', text_lower) for kw in TOXIC_KEYWORDS):
            return {"score": 0.02, "label": "Safe", "is_flagged": False, "toxic_words": []}

    result = _predict_transformer(text)
    if result is None:
        # Absolute fallback if transformer crashes
        keyword_hits = sum(1 for kw in TOXIC_KEYWORDS if re.search(rf'\b{re.escape(kw)}\b', text_lower))
        score = min(1.0, keyword_hits * 0.8)
        result = {"score": score}

    score = result["score"]
    toxic_words = _find_toxic_words(text)

    if toxic_words and score < 0.5:
        score = max(score, 0.7)

    label = _score_to_label(score)
    is_flagged = score >= TOXICITY_THRESHOLD

    return {
        "score": round(score, 4),
        "label": label,
        "is_flagged": is_flagged,
        "toxic_words": toxic_words,
    }


def rewrite_toxic(text: str) -> str:
    result = text
    for toxic, safe in REWRITE_MAP.items():
        pattern = re.compile(re.escape(toxic), re.IGNORECASE)
        result = pattern.sub(safe, result)
    return result


async def analyze(text: str, context: list = None) -> dict:
    ctx_text = _build_context_text(text, context)
    tox = predict_toxicity(ctx_text if context else text)
    rewrite = rewrite_toxic(text) if tox["is_flagged"] else None
    escalation = None
    if context:
        from escalation import predict_escalation
        escalation = predict_escalation(context, tox["score"], tox["is_flagged"])
    return {
        "score": tox["score"],
        "label": tox["label"],
        "is_flagged": tox["is_flagged"],
        "toxic_words": tox.get("toxic_words", []),
        "highlighted_words": tox.get("toxic_words", []),
        "rewrite": rewrite,
        "escalation": escalation,
    }
