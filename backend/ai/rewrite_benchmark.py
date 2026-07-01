import os
import sys
import time
import json
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import ml_service

# Candidate models
MODELS = [
    {"name": "s-nlp/t5-paranmt-detox", "prompt": ""},
    {"name": "google/flan-t5-base", "prompt": "Rewrite the following text to be polite and non-toxic: "},
    {"name": "humarin/chatgpt_paraphraser_on_T5_base", "prompt": "paraphrase: "}
]

TEST_MESSAGES = [
    "You are a stupid idiot and I hate you.",
    "Shut up and get lost, you worthless trash.",
    "This is the most pathetic and disgusting thing I have ever seen.",
    "I am going to kill you, you moron.",
    "You fucking jerk, stop talking to me.",
    "Your code is garbage and you are dumb.",
    "I'm so pissed at you right now.",
    "Die in a fire you scum.",
    "Stop being a retard and fix the bug.",
    "You are an ugly bastard."
]

def check_meaning_preservation(original: str, rewrite: str) -> float:
    # A simple heuristic for meaning preservation: token overlap / similarity
    import difflib
    # It's hard to measure meaning preservation perfectly without an NLI model.
    # difflib gives a basic structural similarity, but paraphrasers change structure.
    # We will just use it as a rough proxy.
    return difflib.SequenceMatcher(None, original.lower(), rewrite.lower()).ratio()

def evaluate_model(model_info):
    print(f"\n==================================================")
    print(f"Evaluating Model: {model_info['name']}")
    print(f"==================================================")
    
    start_load = time.time()
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_info['name'])
        model = AutoModelForSeq2SeqLM.from_pretrained(model_info['name'])
    except Exception as e:
        print(f"Failed to load model {model_info['name']}: {e}")
        return None
        
    print(f"Model loaded in {time.time() - start_load:.2f} seconds.")
    
    total_latency = 0
    total_reduction = 0
    total_meaning = 0
    valid_rewrites = 0
    
    for msg in TEST_MESSAGES:
        # Get original toxicity
        orig_tox = ml_service.predict_toxicity(msg)["score"]
        
        # Generate rewrite
        prompted_msg = model_info["prompt"] + msg
        
        start_gen = time.time()
        inputs = tokenizer(prompted_msg, return_tensors="pt", max_length=128, truncation=True)
        outputs = model.generate(**inputs, max_length=128, num_beams=4, early_stopping=True)
        rewritten_text = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
        gen_time = time.time() - start_gen
        
        # New toxicity
        new_tox = ml_service.predict_toxicity(rewritten_text)["score"]
        reduction = ((orig_tox - new_tox) / orig_tox) * 100 if orig_tox > 0 else 0
        reduction = max(0, reduction)
        
        # Meaning proxy
        meaning_score = check_meaning_preservation(msg, rewritten_text)
        
        total_latency += gen_time
        total_reduction += reduction
        total_meaning += meaning_score
        valid_rewrites += 1
        
        print(f"\nOriginal ({orig_tox:.2f}): {msg}")
        print(f"Rewrite  ({new_tox:.2f}): {rewritten_text}")
        print(f"Reduction: {reduction:.1f}% | Latency: {gen_time*1000:.1f}ms")
    
    if valid_rewrites == 0:
        return None
        
    avg_latency = total_latency / valid_rewrites
    avg_reduction = total_reduction / valid_rewrites
    avg_meaning = total_meaning / valid_rewrites
    
    return {
        "name": model_info["name"],
        "avg_reduction_rate": avg_reduction,
        "avg_latency_ms": avg_latency * 1000,
        "avg_meaning_score": avg_meaning
    }

def run_benchmark():
    results = []
    for m in MODELS:
        res = evaluate_model(m)
        if res:
            results.append(res)
            
    print("\n\n" + "="*50)
    print("FINAL BENCHMARK SUMMARY")
    print("="*50)
    
    if not results:
        print("No models completed successfully.")
        return
        
    for r in results:
        print(f"Model: {r['name']}")
        print(f"  Toxicity Reduction: {r['avg_reduction_rate']:.1f}%")
        print(f"  Average Latency:    {r['avg_latency_ms']:.1f} ms")
        print(f"  Meaning Score:      {r['avg_meaning_score']:.2f}")
        print("-" * 50)
        
    best_model = max(results, key=lambda x: (x["avg_reduction_rate"], -x["avg_latency_ms"]))
    print(f"\nWINNER: {best_model['name']}")
    print("="*50)

if __name__ == "__main__":
    run_benchmark()
