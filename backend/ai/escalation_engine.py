import datetime
from typing import List, Dict, Any

def predict_escalation(messages: List[dict], analytics_result: dict) -> Dict[str, Any]:
    """
    Deterministically predicts the probability of a conversation escalating
    to HIGH or CRITICAL risk based on heuristic trend analysis of the recent messages.
    """
    
    # 1. Initialization
    probability = 0.0
    confidence = 0.0
    reasons = []
    
    # We analyze up to the last 10 messages for trend velocity
    recent_msgs = messages[-10:] if len(messages) >= 10 else messages
    num_recent = len(recent_msgs)
    
    if num_recent == 0:
        return _build_response(0, "LOW", 0.9, "STABLE", [], "Unknown")
        
    # 2. Metric Accumulation
    toxic_count = 0
    consecutive_toxic = 0
    max_consecutive_toxic = 0
    recent_risk_scores = []
    anger_disgust_count = 0
    pii_count = 0
    rewrite_count = 0
    
    for m in recent_msgs:
        is_toxic = m.get("toxicity_score", 0) > 0.5
        if is_toxic:
            toxic_count += 1
            consecutive_toxic += 1
            max_consecutive_toxic = max(max_consecutive_toxic, consecutive_toxic)
        else:
            consecutive_toxic = 0
            
        recent_risk_scores.append(m.get("risk_score", 0))
        
        emo = m.get("emotion", "neutral")
        if emo in ["anger", "disgust", "fear"]:
            anger_disgust_count += 1
            
        if m.get("contains_pii", False):
            pii_count += 1
            
        if m.get("edited", False) or m.get("is_flagged", False): # Approximation for interventions
            rewrite_count += 1

    # 3. Trend Calculations
    risk_trend = 0 # -1 to 1
    if len(recent_risk_scores) > 2:
        first_half_avg = sum(recent_risk_scores[:len(recent_risk_scores)//2]) / max(1, len(recent_risk_scores)//2)
        second_half_avg = sum(recent_risk_scores[len(recent_risk_scores)//2:]) / max(1, len(recent_risk_scores)//2)
        if second_half_avg > first_half_avg + 10:
            risk_trend = 1
        elif second_half_avg < first_half_avg - 10:
            risk_trend = -1
            
    # Velocity calculation (messages per minute)
    velocity = 0
    if num_recent > 1:
        try:
            # Assuming timestamps are standard iso format strings
            t1 = datetime.datetime.fromisoformat(str(recent_msgs[0]["timestamp"]).replace("Z", "+00:00"))
            t2 = datetime.datetime.fromisoformat(str(recent_msgs[-1]["timestamp"]).replace("Z", "+00:00"))
            delta_minutes = max(0.1, (t2 - t1).total_seconds() / 60.0)
            velocity = num_recent / delta_minutes
        except Exception:
            velocity = 1.0 # fallback

    # 4. Weighted Scoring
    score = 0.0
    
    # Toxicity Density (Max 0.3)
    tox_density = toxic_count / num_recent
    score += tox_density * 0.3
    if tox_density > 0.5:
        reasons.append("Toxicity density is exceedingly high in recent messages.")
        
    # Consecutive Toxic (Max 0.15)
    if max_consecutive_toxic >= 2:
        score += min(max_consecutive_toxic * 0.05, 0.15)
        reasons.append(f"Detected {max_consecutive_toxic} consecutive toxic messages.")
        
    # Emotion Shift (Max 0.2)
    emo_density = anger_disgust_count / num_recent
    score += emo_density * 0.2
    if emo_density > 0.4:
        reasons.append("Anger or Disgust has become a dominant emotion.")
        
    # Risk Trend (Max 0.15)
    if risk_trend > 0:
        score += 0.15
        reasons.append("Risk scores are steadily rising.")
        
    # Velocity (Max 0.1)
    if velocity > 5: # more than 5 msgs per min
        score += 0.1
        reasons.append("Message frequency indicates rapid, heated exchange.")
        
    # Interventions (Max 0.1)
    if rewrite_count > 0 or pii_count > 0:
        score += 0.1
        reasons.append("Multiple PII or AI interventions detected recently.")
        
    probability = min(1.0, max(0.0, score))
    
    # 5. Determine State and Trend
    current_health = analytics_result.get("conversation_health_score", 100)
    current_risk = analytics_result.get("average_risk_score", 0)
    
    trend_state = "STABLE"
    if risk_trend > 0 or current_health < 50:
        trend_state = "ESCALATING"
    if current_risk > 80 and risk_trend > 0:
        trend_state = "CRITICAL"
    if risk_trend < 0 and current_health > 70:
        trend_state = "IMPROVING"

    # 6. Confidence Logic
    # High confidence if indicators agree. (e.g. rising risk AND high velocity AND high toxicity)
    indicators_active = sum([1 for x in [risk_trend>0, tox_density>0.3, emo_density>0.3, velocity>5] if x])
    if indicators_active >= 3:
        confidence = 0.95
    elif indicators_active == 2:
        confidence = 0.85
    elif indicators_active == 1:
        confidence = 0.70
    else:
        # If nothing is active but probability is somehow high, it's conflicting
        confidence = 0.90 if probability < 0.2 else 0.50
        
    if probability < 0.2:
        reasons.append("No significant escalation patterns detected.")
        predicted_state = "LOW"
        window = "N/A"
    elif probability < 0.5:
        predicted_state = "MEDIUM"
        window = "5-10 messages"
    elif probability < 0.8:
        predicted_state = "HIGH"
        window = "2-5 messages"
    else:
        predicted_state = "CRITICAL"
        window = "1-2 messages"
        
    # Recommendations
    recommendations = []
    if predicted_state == "LOW":
        recommendations.append({"priority": "LOW", "action": "Continue Monitoring"})
    elif predicted_state == "MEDIUM":
        recommendations.append({"priority": "MEDIUM", "action": "Notify Moderator"})
    elif predicted_state == "HIGH":
        recommendations.append({"priority": "HIGH", "action": "Temporary Mute Recommended"})
    else:
        recommendations.append({"priority": "CRITICAL", "action": "Immediate Moderator Intervention"})

    return _build_response(probability, predicted_state, confidence, trend_state, reasons, window, recommendations)

def _build_response(probability, predicted_state, confidence, trend_state, reasons, window, recommendations=[]):
    return {
        "prediction": {
            "current_state": "UNKNOWN", # will be overwritten by manager
            "predicted_state": predicted_state,
            "probability": round(probability, 2),
            "confidence": round(confidence, 2),
            "expected_window": window,
            "trend": trend_state
        },
        "timeline": {},
        "reasons": reasons,
        "recommendations": recommendations,
        "metadata": {
            "generated_at": datetime.datetime.utcnow().isoformat(),
            "prediction_version": "1.0",
            "analysis_version": "1.0"
        }
    }
