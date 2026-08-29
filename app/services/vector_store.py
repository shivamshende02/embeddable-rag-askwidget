import uuid
from ollama import _client
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from qdrant_client.models import ScoredPoint
from langsmith import traceable
from qdrant_client.models import Distance, VectorParams, PointStruct, ScoredPoint

CACHE_COLLECTION_NAME = "chat_semantic_cache"

def init_cache_collection():
    collections = [c.name for c in _client.get_collections().collections]
    if CACHE_COLLECTION_NAME not in collections:
        _client.create_collection(
            collection_name=CACHE_COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE), # Adjust size based on your embedding model
        )
def search_semantic_cache(query_vector: list[float], score_threshold: float = 0.95) -> str | None:
    init_cache_collection()
    hits = _client.search(
        collection_name=CACHE_COLLECTION_NAME,
        query_vector=query_vector,
        limit=1,
        score_threshold=score_threshold,
    )
    if hits:
        return hits[0].payload.get("answer")
    return None

def store_semantic_cache(question: str, query_vector: list[float], answer: str):
    init_cache_collection()
    import uuid
    point_id = str(uuid.uuid4())
    _client.upsert(
        collection_name=CACHE_COLLECTION_NAME,
        points=[
            PointStruct(
                id=point_id,
                vector=query_vector,
                payload={"question": question, "answer": answer}
            )
        ]
    )        

_client = QdrantClient(url="http://localhost:6333")
COLLECTION_NAME = "documents"
EMBEDDING_DIM = 384  # matches all-MiniLM-L6-v2

def ensure_collection() -> None:
    existing = [c.name for c in _client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        _client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=qmodels.VectorParams(size=EMBEDDING_DIM, distance=qmodels.Distance.COSINE),
        )

def upsert_chunks(document_id: str, chunks: list[str], embeddings: list[list[float]]) -> None:
    points = [
        qmodels.PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={"document_id": document_id, "content": chunk},
        )
        for chunk, vector in zip(chunks, embeddings)
    ]
    _client.upsert(collection_name=COLLECTION_NAME, points=points)


def delete_document_vectors(document_id: str) -> None:
    _client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=qmodels.FilterSelector(
            filter=qmodels.Filter(
                must=[qmodels.FieldCondition(key="document_id", match=qmodels.MatchValue(value=document_id))]
            )
        ),
    )   

def search_similar_chunks(query_vector: list[float], top_k: int = 5, score_threshold: float | None = None) -> list[dict]:
    # Pass score_threshold directly to Qdrant's search method if supported, 
    # or pass it via query_filter / score filter parameters.
    # Qdrant client search typically accepts score_threshold directly:
    search_results = _client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k,
        score_threshold=score_threshold,  # <-- Add this here
    )
    
    formatted_results = []
    for hit in search_results:
        payload = hit.payload or {}
        formatted_results.append({
            "content": payload.get("content", ""),
            "score": hit.score,
            "document_id": payload.get("document_id"),
        })
        
    return formatted_results     

@traceable(name="retrieve_chunks")
def search_similar_chunks(query_vector: list[float], top_k: int = 3, score_threshold: float = 0.3) -> list[dict]:
    search_results = _client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k,
        score_threshold=score_threshold,
    )
    
    formatted_results = []
    for hit in search_results:
        payload = hit.payload or {}
        formatted_results.append({
            "content": payload.get("content", ""),
            "score": hit.score,
            "document_id": payload.get("document_id"),
        })
        
    return formatted_results


