from sentence_transformers import SentenceTransformer

# Loaded once at import time — model stays in memory, reused across requests.
_model = SentenceTransformer("all-MiniLM-L6-v2")  # free, local, 384-dim, fast

def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    return _model.encode(texts, convert_to_numpy=True).tolist()