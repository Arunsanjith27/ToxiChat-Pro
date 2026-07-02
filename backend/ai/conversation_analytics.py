from typing import List

def analyze_conversation(messages: List[dict]) -> dict:
    """
    Aggregates message-level AI metadata into conversation-level analytics.
    Does not perform any AI inference.
    """
    total_messages = len(messages)
    if total_messages == 0:
        return {
            "total_messages": 0,
            "toxic_messages": 0,
            "overall_toxicity_ratio": 0.0,
            "emotion_distribution": {},
            "pii_instances": 0,
            "average_risk_score": 0.0,
            "rewrites_accepted": 0,
            "conversation_health_score": 100,
            "critical_events": [],
            "conversation_state": "HEALTHY"
        }

    toxic_count = 0
    emotion_dist = {}
    pii_count = 0
    total_risk_score = 0
    rewrite_count = 0
    critical_events = []

    for msg in messages:
        # Toxicity
        if msg.get("is_flagged"):
            toxic_count += 1
            
        # Emotion
        emotion = msg.get("emotion", "neutral")
        emotion_dist[emotion] = emotion_dist.get(emotion, 0) + 1
        
        # PII
        if msg.get("contains_pii"):
            pii_count += 1
            
        # Risk
        risk_score = msg.get("risk_score", 0)
        total_risk_score += risk_score
        
        if msg.get("risk_level") == "HIGH":
            event = {
                "id": msg.get("id"),
                "timestamp": msg.get("timestamp"),
                "sender": msg.get("sender"),
                "risk_score": risk_score,
                "reasons": msg.get("risk_reasons", []),
                "explanation": msg.get("explanation", {})
            }
            critical_events.append(event)
            
        # Rewrites
        # A rewrite is counted if the message was edited and originally triggered a rewrite suggestion.
        # Alternatively, since we don't track rewrite usage explicitly, we can count edited toxic messages
        if msg.get("edited") and msg.get("toxicity_score", 0.0) < 0.4:
            # Simple heuristic for a successful rewrite: message was edited and is now non-toxic
            rewrite_count += 1

    avg_risk = int(total_risk_score / total_messages)
    toxicity_ratio = toxic_count / total_messages
    
    # Base health is 100, subtracting based on toxicity ratio and average risk
    health_score = max(0, 100 - (toxicity_ratio * 100) - (avg_risk * 0.5))
    
    # Calculate trend to determine conversation_state
    conversation_state = "STABLE"
    if health_score < 30 or avg_risk > 70:
        conversation_state = "CRITICAL"
    elif total_messages >= 4:
        midpoint = total_messages // 2
        first_half = messages[:midpoint]
        second_half = messages[midpoint:]
        
        fh_risk = sum(m.get("risk_score", 0) for m in first_half) / len(first_half)
        sh_risk = sum(m.get("risk_score", 0) for m in second_half) / len(second_half)
        
        if sh_risk > fh_risk + 15:
            conversation_state = "ESCALATING"
        elif sh_risk < fh_risk - 15:
            conversation_state = "IMPROVING"
        elif health_score > 85:
            conversation_state = "HEALTHY"
    elif health_score > 85:
        conversation_state = "HEALTHY"

    return {
        "total_messages": total_messages,
        "toxic_messages": toxic_count,
        "overall_toxicity_ratio": round(toxicity_ratio, 2),
        "emotion_distribution": emotion_dist,
        "pii_instances": pii_count,
        "average_risk_score": avg_risk,
        "rewrites_accepted": rewrite_count,
        "conversation_health_score": int(health_score),
        "critical_events": critical_events,
        "conversation_state": conversation_state
    }
