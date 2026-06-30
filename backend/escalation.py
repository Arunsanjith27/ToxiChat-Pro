"""Conversation-level toxicity escalation prediction."""

from datetime import datetime
from typing import List, Optional


def predict_escalation(
    recent_messages: List[dict],
    current_score: float,
    current_is_flagged: bool,
) -> dict:
    """
    Predict whether a conversation is escalating toward toxic behavior.
    Uses recent message toxicity scores, trend, and frequency of flags.
    """
    if not recent_messages:
        return {
            "escalation_score": round(current_score * 0.5, 4),
            "escalation_level": "low",
            "is_escalating": False,
            "conversation_health": 100,
            "trend": "stable",
            "reason": "No prior context in this conversation",
        }

    scores = [float(m.get("toxicity_score", 0)) for m in recent_messages[-10:]]
    flagged_count = sum(1 for m in recent_messages[-10:] if m.get("is_flagged"))
    total = len(scores)

    avg_score = sum(scores) / max(total, 1)
    recent_avg = sum(scores[-3:]) / max(min(3, total), 1)
    older_avg = sum(scores[:-3]) / max(total - 3, 1) if total > 3 else avg_score

    trend_delta = recent_avg - older_avg
    if trend_delta > 0.15:
        trend = "rising"
    elif trend_delta < -0.15:
        trend = "falling"
    else:
        trend = "stable"

    escalation_score = min(
        1.0,
        (recent_avg * 0.4)
        + (current_score * 0.3)
        + (flagged_count / max(total, 1) * 0.2)
        + (max(0, trend_delta) * 0.3),
    )

    if current_is_flagged:
        escalation_score = min(1.0, escalation_score + 0.15)

    if escalation_score >= 0.7 or (flagged_count >= 3 and trend == "rising"):
        level = "critical"
        is_escalating = True
        reason = "High toxicity trend with multiple flagged messages"
    elif escalation_score >= 0.45 or (flagged_count >= 2 and trend != "falling"):
        level = "high"
        is_escalating = True
        reason = "Conversation toxicity is increasing"
    elif escalation_score >= 0.25 or flagged_count >= 1:
        level = "medium"
        is_escalating = trend == "rising"
        reason = "Some toxic activity detected in recent messages"
    else:
        level = "low"
        is_escalating = False
        reason = "Conversation appears healthy"

    conversation_health = max(0, min(100, int((1 - escalation_score) * 100)))

    return {
        "escalation_score": round(escalation_score, 4),
        "escalation_level": level,
        "is_escalating": is_escalating,
        "conversation_health": conversation_health,
        "trend": trend,
        "flagged_in_window": flagged_count,
        "recent_avg_toxicity": round(recent_avg, 4),
        "reason": reason,
    }


def compute_reputation(
    total_messages: int,
    toxic_messages: int,
    warnings_count: int,
    mute_count: int = 0,
) -> dict:
    """Compute user reputation score (0-100)."""
    if total_messages == 0:
        score = 100
    else:
        toxic_ratio = toxic_messages / total_messages
        score = 100 - (toxic_ratio * 60) - (warnings_count * 8) - (mute_count * 15)
        score = max(0, min(100, int(score)))

    if score >= 80:
        tier = "excellent"
    elif score >= 60:
        tier = "good"
    elif score >= 40:
        tier = "fair"
    elif score >= 20:
        tier = "poor"
    else:
        tier = "critical"

    return {
        "reputation_score": score,
        "reputation_tier": tier,
        "total_messages": total_messages,
        "toxic_messages": toxic_messages,
    }
