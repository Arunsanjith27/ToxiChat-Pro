def build_structured_context(analytics_result: dict, summary_type: str = "moderator") -> str:
    """
    Builds a dense, structured paragraph from the analytics result.
    This paragraph acts as the 'source text' for the NLP summarization model.
    """
    
    health = analytics_result.get("conversation_health_score", 0)
    state = analytics_result.get("conversation_state", "UNKNOWN")
    avg_risk = analytics_result.get("average_risk_score", 0)
    peak_risk = analytics_result.get("peak_risk_score", 0)
    
    emotions = analytics_result.get("emotion_distribution", {})
    dominant_emotion = max(emotions, key=emotions.get) if emotions else "Neutral"
    
    toxic_ratio = analytics_result.get("overall_toxicity_ratio", 0)
    pii_count = analytics_result.get("pii_instances", 0)
    rewrite_count = analytics_result.get("rewritten_messages", 0)
    
    events = analytics_result.get("critical_events", [])
    
    context = []
    
    if summary_type == "moderator":
        context.append(f"The overall health of the conversation is {health}/100 and it is currently in a {state} state.")
        context.append(f"The average risk score is {avg_risk}, peaking at {peak_risk}.")
        context.append(f"The dominant emotion expressed is {dominant_emotion}.")
        context.append(f"Toxicity was detected in {toxic_ratio*100:.0f}% of messages, with {pii_count} instances of PII exposure and {rewrite_count} messages actively rewritten by AI.")
        if events:
            context.append(f"There were {len(events)} major critical events involving escalation and high risk.")
        context.append("Please provide a concise moderator recommendation based on these factors.")
        
    elif summary_type == "user":
        context.append(f"The conversation was mostly {dominant_emotion}.")
        if health > 80:
            context.append("It was a very healthy and positive discussion.")
        elif health < 40:
            context.append("There was some tension and negative emotion.")
        context.append("Please summarize the main emotional journey and highlights.")
        
    elif summary_type == "incident":
        context.append(f"This is an incident report. The conversation reached a {state} state with a peak risk of {peak_risk}.")
        context.append(f"There were {len(events)} critical events, {pii_count} PII leaks, and {toxic_ratio*100:.0f}% toxicity.")
        context.append("Please generate an incident timeline and final recommendation.")
        
    elif summary_type == "daily" or summary_type == "weekly":
        context.append(f"This is a {summary_type} overview.")
        context.append(f"The average risk was {avg_risk} and health was {health}.")
        context.append(f"The dominant emotion was {dominant_emotion}. We observed {pii_count} PII leaks and {rewrite_count} AI interventions.")
        context.append("Please provide a high-level overview of the statistics.")
        
    else:
        context.append(f"The conversation state is {state} with a health of {health}. Risk averages {avg_risk}.")
        
    return " ".join(context)
