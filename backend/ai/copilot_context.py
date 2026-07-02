import ai.conversation_analytics as conversation_analytics
import ai.escalation_engine as escalation_engine

def build_copilot_context(messages: list) -> dict:
    """
    Aggregates existing intelligence across the AI suite into a single structured context object.
    No heavy models are executed here.
    """
    if not messages:
        return {}

    # 1. Harvest Base Analytics
    analytics = conversation_analytics.analyze_conversation(messages)
    
    # 2. Harvest Predictive Escalation State
    prediction_data = escalation_engine.predict_escalation(messages, analytics)
    
    # 3. Harvest Message-level Insights (Explainability, PII, Emotion, Risk, Rewrites)
    pii_events = []
    rewrites = []
    flagged_reasons = []
    dominant_emotions = {}
    high_risk_messages = []
    
    # Also look for Multimedia evidence (audio/image) in message metadata (simulated here)
    has_image = False
    has_audio = False
    
    for m in messages:
        if m.get("contains_pii"):
            pii_events.append({"sender": m.get("sender"), "timestamp": m.get("timestamp")})
        
        if m.get("edited"):
            rewrites.append({"sender": m.get("sender"), "original": m.get("original_text"), "new": m.get("text")})
            
        if m.get("is_flagged"):
            high_risk_messages.append(m)
            exp = m.get("explanation", {})
            if isinstance(exp, dict):
                for k, v in exp.items():
                    flagged_reasons.append(v)
                    
        emo = m.get("emotion", "neutral")
        dominant_emotions[emo] = dominant_emotions.get(emo, 0) + 1
        
        # In a real impl, we'd check if the message has attachment metadata
        if "[IMAGE]" in m.get("text", ""): has_image = True
        if "[AUDIO]" in m.get("text", ""): has_audio = True

    # 4. Synthesize Context Object
    context = {
        "analytics": analytics,
        "prediction": prediction_data,
        "insights": {
            "pii_exposure_count": len(pii_events),
            "pii_events": pii_events,
            "rewrite_count": len(rewrites),
            "rewrites": rewrites,
            "high_risk_messages": high_risk_messages,
            "explainability_reasons": list(set(flagged_reasons)), # Deduplicate
            "dominant_emotions": dominant_emotions,
            "contains_image_evidence": has_image,
            "contains_audio_evidence": has_audio
        }
    }
    
    return context
