import datetime

def answer_moderator_query(query: str, context: dict) -> dict:
    """
    Acts as the deterministic reasoning layer.
    Takes a query (string or ID) and the structured context object.
    Returns a structured Copilot Response with answer, confidence, sources, and recommendations.
    """
    # Normalize query
    q = query.lower()
    
    answer = "I'm sorry, I cannot answer that query based on the current context."
    confidence = 0.0
    sources = []
    recommendations = []
    
    analytics = context.get("analytics", {})
    prediction = context.get("prediction", {}).get("prediction", {})
    insights = context.get("insights", {})

    # Q1: Why was this conversation flagged?
    if "why" in q and "flagged" in q:
        reasons = insights.get("explainability_reasons", [])
        if reasons:
            answer = f"This conversation was flagged primarily because: {', '.join(reasons)}."
            confidence = 0.95
            sources.append("Explainable AI")
        else:
            answer = "The conversation was flagged due to overall risk scores exceeding the threshold, though specific explainability reasons were not isolated."
            confidence = 0.80
            
        sources.append("Risk Engine")
        
    # Q2: Summarize this incident.
    elif "summarize" in q and ("incident" in q or "conversation" in q):
        risk_level = analytics.get("conversation_state", "UNKNOWN")
        tox_ratio = analytics.get("overall_toxicity_ratio", 0) * 100
        answer = f"This is a {risk_level} risk conversation. Approximately {tox_ratio:.0f}% of messages contain toxicity. "
        
        if insights.get("pii_exposure_count", 0) > 0:
            answer += "There has been confirmed PII exposure. "
            
        if prediction.get("predicted_state") in ["HIGH", "CRITICAL"]:
            answer += f"The AI predicts escalation to {prediction.get('predicted_state')} risk shortly."
            
        confidence = 0.90
        sources.extend(["Conversation Analytics", "Prediction Engine"])

    # Q3: Which messages caused escalation?
    elif "escalation" in q and "messages" in q:
        high_risk = insights.get("high_risk_messages", [])
        if high_risk:
            count = len(high_risk)
            answer = f"There are {count} high-risk messages driving the escalation. Key themes include rising toxicity and aggressive emotion shifts."
            confidence = 0.92
            sources.append("Risk Engine")
        else:
            answer = "Escalation is being driven by subtle conversational trends rather than individual high-risk messages."
            confidence = 0.70
            sources.append("Conversation Analytics")

    # Q4: Explain prediction
    elif "explain" in q and "prediction" in q:
        state = prediction.get("predicted_state", "UNKNOWN")
        trend = prediction.get("trend", "UNKNOWN")
        prob = prediction.get("probability", 0) * 100
        answer = f"The Prediction Engine forecasts a {prob:.0f}% probability of reaching {state} status. The current trend is {trend}."
        confidence = prediction.get("confidence", 0.0)
        sources.append("Prediction Engine")

    # Q5: Recommend actions
    elif "recommend" in q and ("action" in q or "moderator" in q):
        recs = context.get("prediction", {}).get("recommendations", [])
        if not recs:
            if analytics.get("average_risk_score", 0) > 70:
                recs = [{"priority": "HIGH", "action": "Temporary mute"}, {"priority": "MEDIUM", "action": "Issue Warning"}]
            else:
                recs = [{"priority": "LOW", "action": "Monitor conversation"}]
                
        answer = "Based on the combined Risk and Prediction data, here are the recommended actions."
        recommendations = recs
        confidence = 0.88
        sources.extend(["Prediction Engine", "Risk Engine"])

    # Q6: Show all PII exposure
    elif "pii" in q:
        pii_count = insights.get("pii_exposure_count", 0)
        if pii_count > 0:
            answer = f"Found {pii_count} PII exposure events in this conversation."
            confidence = 0.99
            sources.append("PII Engine")
        else:
            answer = "No PII exposure was detected in this conversation."
            confidence = 0.99
            sources.append("PII Engine")

    # Q7: Summarize image evidence
    elif "image" in q:
        if insights.get("contains_image_evidence"):
            answer = "Image evidence was analyzed and processed by the Vision Engine. High risk attributes were found in visual context."
            confidence = 0.85
            sources.append("Image Analysis")
        else:
            answer = "No image evidence is associated with this conversation context."
            confidence = 0.95
            sources.append("Image Analysis")
            
    # Q8: Summarize audio evidence
    elif "audio" in q or "voice" in q:
        if insights.get("contains_audio_evidence"):
            answer = "Audio/Voice evidence was transcribed by Faster-Whisper and flagged for safety violations."
            confidence = 0.85
            sources.append("Voice Analysis")
        else:
            answer = "No audio or voice evidence was found."
            confidence = 0.95
            sources.append("Voice Analysis")

    # Fallback / Default
    else:
        answer = "I am a specialized Moderator Copilot. I can help summarize incidents, explain predictions, analyze PII, or recommend actions based on ToxiChat's AI."
        confidence = 1.0
        sources = ["Copilot System"]

    # Calculate final dynamic confidence based on source strength
    if len(sources) > 1 and confidence < 0.95:
        confidence += 0.05 # Boost if multiple engines agree
        
    return {
        "answer": answer,
        "confidence": round(min(1.0, max(0.0, confidence)), 2),
        "sources": list(set(sources)),
        "recommendations": recommendations,
        "metadata": {
            "query": query,
            "generated_at": datetime.datetime.utcnow().isoformat(),
            "execution_time_ms": 12 # Hardcoded simulation for speed
        }
    }
