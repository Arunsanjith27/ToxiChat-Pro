import os
import time
import psutil
import torch
from transformers import pipeline

def run_benchmark():
    models = [
        "Falconsai/text_summarization",
        "google/flan-t5-base"
    ]
    
    contexts = {
        "Small (20)": "The conversation state is HEALTHY with an average risk score of 10. The dominant emotion is joy. There were 0 toxic messages and 0 PII leaks. The overall health is 95/100. No critical events were detected.",
        "Medium (500)": "The conversation state is ESCALATING with an average risk score of 45. The dominant emotion is anger. There were 15 toxic messages and 2 PII leaks. The overall health is 50/100. 3 critical events were detected involving severe insults and escalation.",
        "Large (5000)": "The conversation state is CRITICAL with an average risk score of 85. The dominant emotion is disgust. There were 450 toxic messages and 12 PII leaks. The overall health is 10/100. 25 critical events were detected involving severe threats, sustained harassment, and multiple policy violations."
    }
    
    results = []
    
    print("Starting Benchmark...")
    
    for model_name in models:
        print(f"\n--- Testing Model: {model_name} ---")
        try:
            start_download = time.time()
            process = psutil.Process(os.getpid())
            mem_before = process.memory_info().rss / (1024 * 1024)
            
            pipe = pipeline("summarization", model=model_name, device=-1) # Force CPU
            
            mem_after = process.memory_info().rss / (1024 * 1024)
            load_time = time.time() - start_download
            
            print(f"[{model_name}] Load Time: {load_time:.2f}s | Memory Footprint: {mem_after - mem_before:.2f} MB")
            
            model_results = {"model": model_name, "memory_mb": mem_after - mem_before, "runs": []}
            
            for size, text in contexts.items():
                start_infer = time.time()
                summary = pipe(text, max_length=50, min_length=10, do_sample=False)
                infer_time = time.time() - start_infer
                
                print(f"[{model_name}] {size} Context -> Latency: {infer_time:.2f}s")
                print(f"Summary: {summary[0]['summary_text']}")
                
                model_results["runs"].append({
                    "size": size,
                    "latency": infer_time,
                    "summary": summary[0]['summary_text']
                })
                
            results.append(model_results)
            
            # Clear memory
            del pipe
            import gc
            gc.collect()
            
        except Exception as e:
            print(f"Failed to benchmark {model_name}: {str(e)}")
            
    print("\n\n--- Final Benchmark Complete ---")
    
if __name__ == "__main__":
    run_benchmark()
