import ml_service
import ai.emotion_service as emotion_service
import ai.pii_service as pii_service
import ai.explainability as explainability
import ai.embedding_service as embedding_service
import ai.conversation_analytics as conversation_analytics
import ai.conversation_intelligence as conversation_intelligence
import ai.image_moderation as image_moderation
import ai.audio_moderation as audio_moderation
import ai.escalation_engine as escalation_engine
import ai.copilot_context as copilot_context
import ai.moderator_copilot as moderator_copilot
import ai.resilience as resilience
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
    emotion_data = await resilience.execute_resilient(
        "Emotion",
        emotion_service.predict_emotion,
        text,
        fallback={"label": "neutral", "confidence": 0.0},
        timeout=3.0,
        retries=1
    )

    # 2. Detect Toxicity (context-aware)
    tox_data = await resilience.execute_resilient(
        "Toxicity",
        ml_service.analyze,
        text,
        context=context,
        fallback={"score": 0.0, "is_flagged": False, "label": "clean", "toxic_words": [], "highlighted_words": []},
        timeout=5.0,
        retries=1
    )

    # 3. Detect PII
    pii_data = await resilience.execute_resilient(
        "PII",
        pii_service.detect_pii,
        text,
        fallback={"contains_pii": False, "entities": []},
        timeout=3.0,
        retries=1
    )

    # 4. Rewrite (conditionally)
    if tox_data.get("is_flagged"):
        rewrite_res = await resilience.execute_resilient(
            "Rewrite",
            rewrite_service.rewrite_message,
            text, tox_data,
            fallback={"rewritten_text": None},
            timeout=5.0,
            retries=0
        )
        tox_data["rewrite"] = rewrite_res.get("rewritten_text") if rewrite_res else None
    else:
        tox_data["rewrite"] = None

    # 5. Merge Results
    tox_data["emotion"] = emotion_data["label"]
    tox_data["emotion_confidence"] = emotion_data["confidence"]
    tox_data["contains_pii"] = pii_data["contains_pii"]
    tox_data["pii_entities"] = pii_data["entities"]

    # 6. Calculate Risk
    risk_data = await resilience.execute_resilient(
        "Risk",
        risk_engine.calculate_message_risk,
        tox_data, context,
        fallback={"risk_score": 0, "risk_level": "UNKNOWN", "risk_reasons": [], "recommendation": "N/A"},
        timeout=2.0,
        retries=0
    )
    tox_data["risk_score"] = risk_data["risk_score"]
    tox_data["risk_level"] = risk_data["risk_level"]
    tox_data["risk_reasons"] = risk_data["risk_reasons"]
    tox_data["recommendation"] = risk_data["recommendation"]

    # 7. Build Explainability
    explanation = await resilience.execute_resilient(
        "Explainability",
        explainability.build_explanation,
        tox_data,
        fallback={},
        timeout=3.0,
        retries=0
    )
    tox_data["explanation"] = explanation

    # 8. Generate Semantic Embedding
    embedding = embedding_service.generate_embedding(text)
    tox_data["embedding"] = embedding

    return tox_data

async def summarize_conversation(conversation_id: str, summary_type: str = "moderator") -> dict:
    """
    Orchestrates the Conversation Intelligence Engine.
    1. Fetches conversation history.
    2. Runs deterministic analytics on it.
    3. Passes to Conversation Intelligence for NLP summarization.
    """
    from database import get_db
    db = await get_db()
    
    # Simple split of conversation_id assuming format user1_user2
    # In a real app we might pass user1 and user2 or have a true conversation_id
    if "_" in conversation_id:
        u1, u2 = conversation_id.split("_", 1)
        # Fetch messages
        cursor = db.messages.find({
            "$or": [
                {"sender": u1, "receiver": u2},
                {"sender": u2, "receiver": u1}
            ]
        }, {"_id": 0}).sort("timestamp", 1)
        messages = await cursor.to_list(length=1000)
    else:
        # Group fallback
        cursor = db.messages.find({"receiver": conversation_id}, {"_id": 0}).sort("timestamp", 1)
        messages = await cursor.to_list(length=1000)
        
    if not messages:
        return {
            "summary_text": "No messages found for this conversation.",
            "model_used": "None",
            "generation_time_ms": 0,
            "conversation_health": 0,
            "risk_level": "UNKNOWN",
            "dominant_emotion": "Neutral",
            "recommendation": "No action required."
        }
        
    # 2. Run Analytics
    analytics_res = await resilience.execute_resilient(
        "Conversation Analytics",
        conversation_analytics.analyze_conversation,
        messages,
        fallback={"total_messages": len(messages), "conversation_health_score": 0, "conversation_state": "UNKNOWN", "average_risk_score": 0, "overall_toxicity_ratio": 0.0},
        timeout=5.0,
        retries=1
    )
    
    # 3. Generate Generative AI Summary
    summary_result = await resilience.execute_resilient(
        "Conversation Intelligence",
        conversation_intelligence.generate_summary,
        messages, analytics_res, summary_type,
        fallback={
            "summary_text": "Summary generation failed or timed out.",
            "model_used": "None",
            "generation_time_ms": 0,
            "conversation_health": analytics_res.get("conversation_health_score", 0),
            "risk_level": "UNKNOWN",
            "dominant_emotion": "Neutral",
            "recommendation": "Manual review recommended due to system failure."
        },
        timeout=60.0,
        retries=1
    )
    
    return summary_result

async def analyze_conversation_orchestrator(conversation_id: str) -> dict:
    """
    Orchestrates the Conversation Analytics Engine.
    Fetches the conversation history and passes it to the analytics engine.
    """
    from database import get_db
    db = await get_db()
    
    if "_" in conversation_id:
        u1, u2 = conversation_id.split("_", 1)
        cursor = db.messages.find({
            "$or": [
                {"sender": u1, "receiver": u2},
                {"sender": u2, "receiver": u1}
            ]
        }, {"_id": 0}).sort("timestamp", 1)
        messages = await cursor.to_list(length=1000)
    else:
        cursor = db.messages.find({"receiver": conversation_id}, {"_id": 0}).sort("timestamp", 1)
        messages = await cursor.to_list(length=1000)
        
    if not messages:
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
        
    analytics_res = await resilience.execute_resilient(
        "Conversation Analytics",
        conversation_analytics.analyze_conversation,
        messages,
        fallback={
            "total_messages": len(messages),
            "toxic_messages": 0,
            "overall_toxicity_ratio": 0.0,
            "emotion_distribution": {},
            "pii_instances": 0,
            "average_risk_score": 0.0,
            "rewrites_accepted": 0,
            "conversation_health_score": 100,
            "critical_events": [],
            "conversation_state": "UNKNOWN"
        },
        timeout=5.0,
        retries=1
    )
    return analytics_res

async def analyze_image_orchestrator(file_bytes: bytes, mime_type: str) -> dict:
    """
    Orchestrates the entire image moderation pipeline.
    """
    # 1. Validate & Hash
    img_hash = image_moderation.validate_and_hash_image(file_bytes, mime_type)
    
    # In a real database we would check if img_hash exists here
    # For now, we proceed to analysis (mocking the cache miss)
    
    # Write bytes to temp file since CV models usually take file paths
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
        
    try:
        # 2. Extract OCR & Vision
        raw_image_data = await resilience.execute_resilient(
            "Image Moderation",
            image_moderation.analyze_image_content,
            tmp_path,
            fallback={"ocr": {}, "vision": {}},
            timeout=20.0,
            retries=0
        )
        
        # 3. Route OCR to deep text pipeline if text exists
        text_analysis = {}
        risk_data = {"overall_risk": "LOW", "risk_score": 0}
        explanation = {}
        
        extracted_text = raw_image_data["ocr"].get("text", "").strip()
        if extracted_text:
            # We treat the OCR text exactly like a message
            text_analysis = await analyze_message(extracted_text, context=None)
            
            # The text pipeline already runs risk & explainability, but we can augment it
            # with Vision scores
            
            # Merge text analysis outputs
            risk_data["risk_score"] = text_analysis.get("risk_score", 0)
            risk_data["overall_risk"] = text_analysis.get("risk_level", "LOW")
            risk_data["recommendation"] = text_analysis.get("recommendation", "N/A")
            explanation = text_analysis.get("explanation", {})
            
        # Add Vision risk heuristic
        if raw_image_data["vision"].get("nsfw_score", 0) > 0.6:
            risk_data["risk_score"] = max(risk_data["risk_score"], 90)
            risk_data["overall_risk"] = "CRITICAL"
            explanation["vision_alert"] = "High NSFW confidence detected in image."
            
        # 4. Construct unified response
        unified_response = {
            "image": {
                "hash": img_hash,
                "mime_type": mime_type,
                "size_bytes": len(file_bytes)
            },
            "ocr": raw_image_data["ocr"],
            "vision": raw_image_data["vision"],
            "text_analysis": {
                "toxicity": text_analysis.get("score"),
                "emotion": text_analysis.get("emotion"),
                "contains_pii": text_analysis.get("contains_pii")
            } if text_analysis else {},
            "risk": risk_data,
            "explanation": explanation
        }
        return unified_response
    finally:
        os.remove(tmp_path)


async def analyze_audio_orchestrator(file_bytes: bytes, mime_type: str) -> dict:
    """
    Orchestrates the entire audio moderation pipeline.
    """
    # 1. Validate & Hash
    audio_hash = audio_moderation.validate_and_hash_audio(file_bytes, mime_type)
    
    # In a real database we would check if audio_hash exists here
    
    # Write bytes to temp file since Whisper models usually take file paths
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
        
    try:
        # 2. Extract Speech-to-Text & Metadata
        raw_audio_data = await resilience.execute_resilient(
            "Audio Moderation",
            audio_moderation.analyze_audio_content,
            tmp_path,
            fallback={"transcript": {}, "metadata": {}},
            timeout=30.0,
            retries=0
        )
        
        # 3. Route Transcript to deep text pipeline
        text_analysis = {}
        risk_data = {"overall_risk": "LOW", "risk_score": 0}
        explanation = {}
        
        extracted_text = raw_audio_data["transcript"].get("text", "").strip()
        if extracted_text:
            text_analysis = await analyze_message(extracted_text, context=None)
            
            risk_data["risk_score"] = text_analysis.get("risk_score", 0)
            risk_data["overall_risk"] = text_analysis.get("risk_level", "LOW")
            explanation = text_analysis.get("explanation", {})
            
        # 4. Construct unified response
        unified_response = {
            "audio": {
                "hash": audio_hash,
                "mime_type": mime_type,
                "size_bytes": len(file_bytes),
                "duration": raw_audio_data["metadata"].get("duration", 0),
                "language": raw_audio_data["metadata"].get("language", "unknown")
            },
            "transcript": raw_audio_data["transcript"],
            "text_analysis": {
                "toxicity": text_analysis.get("toxicity_score"),
                "emotion": text_analysis.get("emotion"),
                "contains_pii": text_analysis.get("contains_pii")
            } if text_analysis else {},
            "risk": risk_data,
            "explanation": explanation,
            "metadata": raw_audio_data["metadata"]
        }
        return unified_response
    finally:
        os.remove(tmp_path)


async def predict_conversation_escalation(conversation_id: str) -> dict:
    """
    Predicts if a conversation will escalate to HIGH or CRITICAL risk.
    Uses cached analytics and passes to the escalation engine.
    """
    from database import get_db
    db = await get_db()
    
    # 1. Fetch messages (last 50 for deep context)
    if "_" in conversation_id:
        u1, u2 = conversation_id.split("_", 1)
        cursor = db.messages.find({
            "$or": [
                {"sender": u1, "receiver": u2},
                {"sender": u2, "receiver": u1}
            ]
        }, {"_id": 0}).sort("timestamp", 1)
        messages = await cursor.to_list(length=50)
    else:
        cursor = db.messages.find({"receiver": conversation_id}, {"_id": 0}).sort("timestamp", 1)
        messages = await cursor.to_list(length=50)
        
    if not messages:
        return escalation_engine._build_response(0, "LOW", 0, "STABLE", ["No messages"], "N/A")
        
    # 2. Base Analytics (this would normally be cached/retrieved)
    analytics_res = await resilience.execute_resilient(
        "Conversation Analytics",
        conversation_analytics.analyze_conversation,
        messages,
        fallback={
            "conversation_state": "UNKNOWN",
            "average_risk_score": 0
        },
        timeout=5.0,
        retries=1
    )
    
    # 3. Hybrid Prediction Engine
    prediction = await resilience.execute_resilient(
        "Prediction",
        escalation_engine.predict_escalation,
        messages, analytics_res,
        fallback=escalation_engine._build_response(0, "LOW", 0, "STABLE", ["Prediction failed"], "N/A"),
        timeout=5.0,
        retries=0
    )
    
    # Update current state strictly from analytics
    prediction["prediction"]["current_state"] = analytics_res.get("conversation_state", "UNKNOWN")
    
    # Mock Timeline (In production this would trace historical predictions)
    prediction["timeline"] = {
        "snapshots": [
            {"time": "10 mins ago", "risk": 20},
            {"time": "5 mins ago", "risk": 45},
            {"time": "Now", "risk": analytics_res.get("average_risk_score", 0)}
        ]
    }
    
    return prediction

async def ask_moderator_copilot(conversation_id: str, question: str) -> dict:
    """
    Acts as the entry point for AI Moderator Copilot queries.
    Builds context and passes it to the Reasoning Layer.
    """
    from database import get_db
    db = await get_db()
    
    if "_" in conversation_id:
        u1, u2 = conversation_id.split("_", 1)
        cursor = db.messages.find({
            "$or": [
                {"sender": u1, "receiver": u2},
                {"sender": u2, "receiver": u1}
            ]
        }, {"_id": 0}).sort("timestamp", 1)
        messages = await cursor.to_list(length=100)
    else:
        cursor = db.messages.find({"receiver": conversation_id}, {"_id": 0}).sort("timestamp", 1)
        messages = await cursor.to_list(length=100)
        
    if not messages:
        return {
            "answer": "There are no messages in this conversation context.",
            "confidence": 1.0,
            "sources": [],
            "recommendations": [],
            "metadata": {}
        }
        
    # 1. Build Comprehensive Context
    context = await resilience.execute_resilient(
        "Copilot Context",
        copilot_context.build_copilot_context,
        messages,
        fallback="Context generation failed.",
        timeout=5.0,
        retries=1
    )
    
    # 2. Copilot Reasoning Layer
    response = await resilience.execute_resilient(
        "Moderator Copilot",
        moderator_copilot.answer_moderator_query,
        question, context,
        fallback={
            "answer": "Copilot reasoning failed or timed out.",
            "confidence": 0.0,
            "sources": [],
            "recommendations": [],
            "metadata": {}
        },
        timeout=15.0,
        retries=0
    )
    
    return response
