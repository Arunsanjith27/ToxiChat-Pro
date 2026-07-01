import asyncio
import time
import json
import os
import sys

# Add backend to path so imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.manager import analyze_message

# Generate 200 test messages
TEST_MESSAGES = []

# Safe & Joy (50)
joy_words = ["happy", "wonderful", "great", "amazing", "love", "fantastic", "excellent", "awesome", "beautiful", "yay"]
for i in range(50):
    TEST_MESSAGES.append({
        "text": f"I feel so {joy_words[i % 10]} today! It is a {joy_words[(i+1) % 10]} day.",
        "expected_toxicity": False,
        "expected_emotion": "joy"
    })

# Safe & Sadness (50)
sad_words = ["sad", "depressed", "unhappy", "cry", "sorry", "miserable", "terrible", "bad", "lost", "heartbroken"]
for i in range(50):
    TEST_MESSAGES.append({
        "text": f"I am feeling really {sad_words[i % 10]}. Everything is {sad_words[(i+1) % 10]}.",
        "expected_toxicity": False,
        "expected_emotion": "sadness"
    })

# Toxic & Anger (50)
anger_words = ["angry", "furious", "mad", "hate", "annoyed", "frustrated", "pissed", "rage", "irritated", "enraged"]
toxic_words = ["stupid", "idiot", "dumb", "moron", "trash", "loser", "ugly", "pathetic", "worthless", "scum"]
for i in range(50):
    TEST_MESSAGES.append({
        "text": f"I am so {anger_words[i % 10]}, you are a {toxic_words[(i+1) % 10]}! I {anger_words[(i+2) % 10]} you.",
        "expected_toxicity": True,
        "expected_emotion": "anger"
    })

# Safe & Neutral (50)
neutral_sentences = [
    "I will go to the store today.",
    "The weather is cloudy.",
    "Please send me the report.",
    "I ate breakfast at 8 AM.",
    "This is a test message.",
    "He is reading a book.",
    "They went to the park.",
    "Can you call me later?",
    "The train arrives in 5 minutes.",
    "I am working on my project."
]
for i in range(50):
    TEST_MESSAGES.append({
        "text": neutral_sentences[i % 10],
        "expected_toxicity": False,
        "expected_emotion": "neutral"
    })

async def run_benchmark():
    print(f"Starting AI Benchmark with {len(TEST_MESSAGES)} messages...")
    start_time = time.time()
    
    correct_toxicity = 0
    correct_emotion = 0

    for idx, msg in enumerate(TEST_MESSAGES):
        text = msg["text"]
        result = await analyze_message(text)
        
        is_toxic_pred = result.get("is_flagged", False)
        emotion_pred = result.get("emotion", "neutral")
        
        if is_toxic_pred == msg["expected_toxicity"]:
            correct_toxicity += 1
            
        if emotion_pred == msg["expected_emotion"]:
            correct_emotion += 1
            
        if (idx + 1) % 50 == 0:
            print(f"Processed {idx + 1}/{len(TEST_MESSAGES)} messages...")

    end_time = time.time()
    total_time = end_time - start_time
    avg_latency = total_time / len(TEST_MESSAGES)
    
    print("\n" + "="*50)
    print("BENCHMARK RESULTS")
    print("="*50)
    print(f"Total Messages Processed: {len(TEST_MESSAGES)}")
    print(f"Total Time: {total_time:.2f} seconds")
    print(f"Average Latency: {avg_latency*1000:.2f} ms/message")
    print(f"Toxicity Accuracy: {(correct_toxicity / len(TEST_MESSAGES)) * 100:.2f}%")
    print(f"Emotion Accuracy: {(correct_emotion / len(TEST_MESSAGES)) * 100:.2f}%")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(run_benchmark())
