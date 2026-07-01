import ml_service
import ai.emotion_service as emotion_service

async def analyze_message(text: str, context: list = None) -> dict:
    """
    Orchestrates the AI services for an incoming message.
    1. Detects emotion
    2. Detects toxicity
    3. Merges the results
    """
    # 1. Detect Emotion
    emotion_data = emotion_service.predict_emotion(text)

    # 2. Detect Toxicity (context-aware)
    tox_data = await ml_service.analyze(text, context=context)

    # 3. Merge Results
    # tox_data already contains: score, label, is_flagged, toxic_words, highlighted_words, rewrite, escalation
    tox_data["emotion"] = emotion_data["label"]
    tox_data["emotion_confidence"] = emotion_data["confidence"]

    return tox_data
