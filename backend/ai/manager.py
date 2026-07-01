import ml_service
import ai.emotion_service as emotion_service
import ai.pii_service as pii_service
import ai.rewrite_service as rewrite_service
import ai.risk_engine as risk_engine

async def analyze_message(text: str, context: list = None) -> dict:
    """
    Orchestrates the AI services for an incoming message.
    1. Detect Emotion
    2. Detect Toxicity
    3. Detect PII
    4. Merge the results
    """
    # 1. Detect Emotion
    emotion_data = emotion_service.predict_emotion(text)

    # 2. Detect Toxicity (context-aware)
    tox_data = await ml_service.analyze(text, context=context)

    # 3. Detect PII
    pii_data = pii_service.detect_pii(text)

    # 4. Rewrite (conditionally)
    if tox_data.get("is_flagged"):
        rewrite_res = rewrite_service.rewrite_message(text, tox_data)
        tox_data["rewrite"] = rewrite_res.get("rewritten_text")
    else:
        tox_data["rewrite"] = None

    # 5. Merge Results
    # tox_data already contains: score, label, is_flagged, toxic_words, highlighted_words, rewrite, escalation
    tox_data["emotion"] = emotion_data["label"]
    tox_data["emotion_confidence"] = emotion_data["confidence"]
    tox_data["contains_pii"] = pii_data["contains_pii"]
    tox_data["pii_entities"] = pii_data["entities"]

    # 6. Calculate Risk
    risk_data = risk_engine.calculate_message_risk(tox_data, context)
    tox_data["risk_score"] = risk_data["risk_score"]
    tox_data["risk_level"] = risk_data["risk_level"]
    tox_data["risk_reasons"] = risk_data["risk_reasons"]
    tox_data["recommendation"] = risk_data["recommendation"]

    return tox_data
