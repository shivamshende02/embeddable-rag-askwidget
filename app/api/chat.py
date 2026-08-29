import ollama
from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.embeddings import embed_texts 
from app.services.vector_store import search_similar_chunks

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    # 1. Embed the user's question
    query_vector = embed_texts([payload.question])[0]
    
    # 2. Search for similar chunks with a strict score threshold
    results = search_similar_chunks(query_vector=query_vector, top_k=3, score_threshold=0.3)
    
    # 3. Refuse to generate a free-form answer if no relevant context was found
    if not results:
        return ChatResponse(
            answer="I don't have enough information in the knowledge base to answer that question.",
            results=[]
        )
    
    # 4. Build context string from the retrieved chunks
    context = "\n\n".join(r["content"] for r in results)
    
    # 5. Construct prompt with system boundaries
    system_prompt = (
        "You are a helpful AI assistant. Answer the user's question "
        "using ONLY the provided context below. Do not use outside knowledge."
    )
    user_prompt = f"Context:\n{context}\n\nUser Question: {payload.question}"

    # 6. Call local Ollama model
    response = ollama.chat(
        model="llama3.1",  # or your preferred lightweight model like "phi3"
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )

    answer_text = response["message"]["content"]

    return ChatResponse(answer=answer_text, results=results)