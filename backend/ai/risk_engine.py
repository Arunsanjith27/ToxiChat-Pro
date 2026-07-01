def get_risk_level(score: int) -> str:
    if score <= 24:
        return "LOW"
    elif score <= 49:
        return "MEDIUM"
    elif score <= 74:
        return "HIGH"
    else:
        return "CRITICAL"


def generate_recommendation(level: str, reasons: list) -> str:
    if level == "CRITICAL":
        return "Rewrite before sending."
    elif level == "HIGH":
        return "Consider revising your message to soften the tone."
    elif level == "MEDIUM":
        if any("PII" in r for r in reasons):
            return "Remove personal information before sending."
        return "Message is okay, but could be friendlier."
    return "Safe to send."


def calculate_conversation_risk(context: list) -> int:
    """
    Evaluates the risk factor of the conversation history (last 10 messages).
    Returns a score from 0-100 based on escalating toxicity.
    """
    if not context:
        return 0
        
    recent_msgs = context[-10:]
    toxic_count = sum(1 for m in recent_msgs if getattr(m, "is_flagged", False) or m.get("is_flagged", False))
    
    # 0 to 10 toxic messages out of 10 scales to 0-100
    risk = (toxic_count / 10.0) * 100
    return min(100, int(risk))


def calculate_message_risk(analysis: dict, context: list = None) -> dict:
    """
    Calculates the deterministic risk score (0-100) based on AI components:
    Toxicity: 50%
    Emotion: 20%
    PII: 15%
    Conversation History: 10%
    Rewrite Failure: 5%
    """
    score = 0.0
    reasons = []
    
    # 1. Toxicity (50%)
    tox_val = analysis.get("score", 0.0)
    tox_score = tox_val * 50.0
    score += tox_score
    if tox_val > 0.5:
        reasons.append(f"High toxicity detected ({(tox_val*100):.1f}%).")
        
    # 2. Emotion (20%)
    emotion = analysis.get("emotion", "neutral").lower()
    if emotion in ["anger", "disgust"]:
        score += 20.0
        reasons.append(f"Negative emotion ({emotion}) detected.")
    elif emotion in ["fear", "sadness"]:
        score += 10.0
        reasons.append(f"Concerning emotion ({emotion}) detected.")
        
    # 3. PII (15%)
    if analysis.get("contains_pii", False):
        score += 15.0
        reasons.append("Personal Identifiable Information (PII) detected.")
        
    # 4. Conversation History (10%)
    hist_risk = calculate_conversation_risk(context)
    score += (hist_risk / 100.0) * 10.0
    if hist_risk > 50:
        reasons.append("Conversation history shows escalating toxicity.")
        
    # 5. Rewrite Failure (5%)
    # If it was flagged for toxicity but the rewrite is None (rejected or failed)
    if analysis.get("is_flagged", False) and not analysis.get("rewrite"):
        score += 5.0
        reasons.append("AI Rewrite failed or was rejected by safety validation.")
        
    final_score = min(100, int(score))
    level = get_risk_level(final_score)
    rec = generate_recommendation(level, reasons)
    
    return {
        "risk_score": final_score,
        "risk_level": level,
        "risk_reasons": reasons,
        "recommendation": rec
    }
