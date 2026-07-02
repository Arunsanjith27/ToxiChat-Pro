def build_explanation(analysis_data: dict) -> dict:
    """
    Builds a structured Explainable AI (XAI) output based on the raw AI analysis.
    """
    toxicity_score = analysis_data.get("score", 0.0)
    emotion = analysis_data.get("emotion", "neutral")
    contains_pii = analysis_data.get("contains_pii", False)
    pii_entities = analysis_data.get("pii_entities", [])
    risk_level = analysis_data.get("risk_level", "LOW")
    risk_score = analysis_data.get("risk_score", 0)
    risk_reasons = analysis_data.get("risk_reasons", [])

    confidence = 0.95
    if toxicity_score > 0.8 or toxicity_score < 0.2:
        confidence = 0.98

    primary_reasons = []
    recommendations = []
    severity_breakdown = {
        "toxicity": "LOW",
        "emotion": "LOW",
        "pii": "LOW",
        "conversation": risk_level
    }

    if toxicity_score >= 0.7:
        severity_breakdown["toxicity"] = "HIGH"
        primary_reasons.append({
            "category": "toxicity",
            "message": "Highly toxic language detected.",
            "severity": "HIGH"
        })
        recommendations.append("Rewrite recommended.")
        recommendations.append("Moderator review suggested.")
    elif toxicity_score >= 0.4:
        severity_breakdown["toxicity"] = "MEDIUM"
        primary_reasons.append({
            "category": "toxicity",
            "message": "Potentially harmful or aggressive tone detected.",
            "severity": "MEDIUM"
        })
        recommendations.append("Consider rephrasing for a more constructive tone.")

    if emotion in ["anger", "fear", "sadness"]:
        sev = "HIGH" if emotion == "anger" else "MEDIUM"
        severity_breakdown["emotion"] = sev
        primary_reasons.append({
            "category": "emotion",
            "message": f"Strong emotional tone detected ({emotion}).",
            "severity": sev
        })
        if emotion == "anger":
            recommendations.append("Take a moment before sending angry messages.")

    if contains_pii:
        severity_breakdown["pii"] = "HIGH"
        entity_types = list(set([e.get("entity_type", "UNKNOWN") for e in pii_entities]))
        primary_reasons.append({
            "category": "pii",
            "message": f"Personal Information detected ({', '.join(entity_types)}).",
            "severity": "HIGH"
        })
        recommendations.append("Remove sensitive information before sending.")

    for reason in risk_reasons:
        primary_reasons.append({
            "category": "conversation",
            "message": reason,
            "severity": risk_level
        })

    if not primary_reasons:
        primary_reasons.append({
            "category": "general",
            "message": "Message complies with all community guidelines.",
            "severity": "LOW"
        })
        recommendations.append("Safe to send.")

    recommendations = list(dict.fromkeys(recommendations))

    return {
        "overall_risk": risk_level,
        "risk_score": risk_score,
        "confidence": confidence,
        "primary_reasons": primary_reasons,
        "recommendations": recommendations,
        "severity_breakdown": severity_breakdown
    }
