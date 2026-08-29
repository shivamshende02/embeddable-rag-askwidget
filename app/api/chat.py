from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse
# Assuming embed_texts is imported from your embedding service module
from app.services.embeddings import embed_texts 
from app.services.vector_store import search_similar_chunks

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    # 1. Embed the user's question using the same embedding service
    question_embeddings = embed_texts([payload.question])
    query_vector = question_embeddings[0]
    
    # 2. Query Qdrant for similar chunks
    search_results = search_similar_chunks(query_vector=query_vector, top_k=5)
    
    # 3. Return the results
    return ChatResponse(results=search_results)