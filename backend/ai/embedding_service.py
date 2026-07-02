import os
import math
from typing import List

try:
    from sentence_transformers import SentenceTransformer
    # We use all-MiniLM-L6-v2 because it is very fast and lightweight for real-time chat embedding.
    _model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    _model = None
    with open("embedding_load_error.txt", "w") as f:
        f.write(str(e))
    print(f"WARNING: sentence-transformers failed to load: {e}")

def generate_embedding(text: str) -> List[float]:
    """
    Generates a dense vector embedding for a given string of text.
    Returns an empty list if the model is not loaded.
    """
    with open("embedding_debug.log", "a") as f:
        f.write(f"[DEBUG Embedding] generate_embedding called with text: {text}\n")
        f.write(f"[DEBUG Embedding] _model is: {_model}\n")
    if not _model or not text.strip():
        with open("embedding_debug.log", "a") as f:
            f.write(f"[DEBUG Embedding] Returning empty. _model={_model}, text={text}\n")
        return []
    
    try:
        # Encode returns a numpy array, we convert it to a native Python list of floats
        vector = _model.encode(text)
        print(f"[DEBUG Embedding] Generated vector of length: {len(vector)}")
        return vector.tolist()
    except Exception as e:
        print(f"[DEBUG Embedding] Exception during encode: {e}")
        raise

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculates the cosine similarity between two vector embeddings.
    Returns a float between -1.0 and 1.0.
    """
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
        
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
        
    return dot_product / (magnitude1 * magnitude2)
