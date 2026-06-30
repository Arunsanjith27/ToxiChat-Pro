import pytest
from escalation import predict_escalation, compute_reputation


def test_compute_reputation_perfect():
    rep = compute_reputation(100, 0, 0)
    assert rep["reputation_score"] == 100
    assert rep["reputation_tier"] == "excellent"


def test_compute_reputation_toxic():
    rep = compute_reputation(10, 8, 2, 1)
    assert rep["reputation_score"] < 50
    assert rep["reputation_tier"] in ("poor", "critical", "fair")


def test_predict_escalation_rising():
    msgs = [
        {"toxicity_score": 0.2, "is_flagged": False},
        {"toxicity_score": 0.4, "is_flagged": False},
        {"toxicity_score": 0.6, "is_flagged": True},
        {"toxicity_score": 0.8, "is_flagged": True},
    ]
    result = predict_escalation(msgs, 0.85, True)
    assert result["escalation_level"] in ("high", "critical", "medium")
    assert result["conversation_health"] < 100


def test_predict_escalation_healthy():
    result = predict_escalation([], 0.05, False)
    assert result["escalation_level"] == "low"
    assert result["conversation_health"] == 100
