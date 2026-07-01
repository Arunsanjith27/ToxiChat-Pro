import asyncio
import time
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.pii_service import detect_pii

# 10 categories, 20 messages each = 200 messages total
# Phone Numbers, Emails, Aadhaar, PAN, Credit Cards, Bank Accounts, UPI IDs, Passport Numbers, Driving Licenses, Addresses, Mixed Messages, No PII

TEST_MESSAGES = []

# 1. Phone Numbers (20)
for i in range(20):
    TEST_MESSAGES.append({
        "text": f"Call me at +1 (555) {1000+i}-{5000+i}.",
        "has_pii": True
    })

# 2. Emails (20)
for i in range(20):
    TEST_MESSAGES.append({
        "text": f"Send the report to user{i}@example.com by tomorrow.",
        "has_pii": True
    })

# 3. Aadhaar (20)
for i in range(20):
    TEST_MESSAGES.append({
        "text": f"My Aadhaar card number is {1234+i} {5678+i} {9012+i}.",
        "has_pii": True
    })

# 4. PAN (20)
for i in range(20):
    TEST_MESSAGES.append({
        "text": f"The company PAN is ABCDE{1234+i}F.",
        "has_pii": True
    })

# 5. Credit Cards (20)
for i in range(20):
    TEST_MESSAGES.append({
        "text": f"Can you use my card? It's 4111 {1111+i} {2222+i} {3333+i}.",
        "has_pii": True
    })

# 6. Bank Accounts (20)
for i in range(20):
    TEST_MESSAGES.append({
        "text": f"Please transfer to account {10000000000+i} at HDFC.",
        "has_pii": True
    })

# 7. UPI IDs (20)
for i in range(20):
    TEST_MESSAGES.append({
        "text": f"You can pay me at user{i}@okicici or 987654321{i % 10}@ybl.",
        "has_pii": True
    })

# 8. Passport Numbers (20)
for i in range(20):
    TEST_MESSAGES.append({
        "text": f"My passport number is Z{123456+i} issued in New Delhi.",
        "has_pii": True
    })

# 9. Driving Licenses (20)
for i in range(20):
    TEST_MESSAGES.append({
        "text": f"DL number is MH-12 {20101234567+i} for reference.",
        "has_pii": True
    })

# 10. Addresses (20)
for i in range(20):
    TEST_MESSAGES.append({
        "text": f"Deliver it to {10+i} Main Street, Apartment {i}, Springfield, IL 62701.",
        "has_pii": True
    })

# 11. Mixed Messages (20) - Extra PII category
for i in range(20):
    TEST_MESSAGES.append({
        "text": f"Contact john{i}@test.com or call 987-654-{3000+i}.",
        "has_pii": True
    })

# 12. No PII (40) - Ensure we have plenty of negative examples to test precision
for i in range(40):
    TEST_MESSAGES.append({
        "text": f"The weather today is really nice. I think I'll go for a walk {i} times.",
        "has_pii": False
    })


def run_benchmark():
    print(f"Starting PII AI Benchmark with {len(TEST_MESSAGES)} messages...")
    start_time = time.time()
    
    true_positives = 0
    false_positives = 0
    true_negatives = 0
    false_negatives = 0

    for idx, msg in enumerate(TEST_MESSAGES):
        text = msg["text"]
        result = detect_pii(text)
        
        predicted_pii = result.get("contains_pii", False)
        actual_pii = msg["has_pii"]
        
        if actual_pii and predicted_pii:
            true_positives += 1
        elif not actual_pii and not predicted_pii:
            true_negatives += 1
        elif not actual_pii and predicted_pii:
            false_positives += 1
        elif actual_pii and not predicted_pii:
            false_negatives += 1
            
        if (idx + 1) % 50 == 0:
            print(f"Processed {idx + 1}/{len(TEST_MESSAGES)} messages...")

    end_time = time.time()
    total_time = end_time - start_time
    avg_latency = total_time / len(TEST_MESSAGES)
    
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    print("\n" + "="*50)
    print("PII BENCHMARK RESULTS")
    print("="*50)
    print(f"Total Messages Processed: {len(TEST_MESSAGES)}")
    print(f"Total Time: {total_time:.2f} seconds")
    print(f"Average Latency: {avg_latency*1000:.2f} ms/message")
    print("-" * 50)
    print(f"True Positives: {true_positives}")
    print(f"True Negatives: {true_negatives}")
    print(f"False Positives: {false_positives}")
    print(f"False Negatives: {false_negatives}")
    print("-" * 50)
    print(f"Precision: {precision * 100:.2f}%")
    print(f"Recall:    {recall * 100:.2f}%")
    print(f"F1 Score:  {f1_score * 100:.2f}%")
    print("="*50)

if __name__ == "__main__":
    run_benchmark()
