import ollama
from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.embeddings import embed_texts 
from app.services.vector_store import search_similar_chunks

router = APIRouter(prefix="/chat", tags=["chat"])

# Minimum similarity score required to consider chunks relevant (adjust based on your embedding model, e.g., 0.3 or 0.4)
RELEVANCE_THRESHOLD = 0.35

@router.post("/", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    # 1. Embed the user's question
    question_embeddings = embed_texts([payload.question])
    query_vector = question_embeddings[0]
    
    # 2. Retrieve top similar chunks from Qdrant
    search_results = search_similar_chunks(query_vector=query_vector, top_k=3)
    
    # 3. Check if we found any relevant chunks based on score
    # If no results or the best score is below our threshold, block it before hitting LLM!
    if not search_results or search_results[0]["score"] < RELEVANCE_THRESHOLD:
        return ChatResponse(
            answer="I'm sorry, but I can only answer questions based on the uploaded documents. That query is outside my knowledge base.",
            results=[]
        )
    
    # 4. Build context string ONLY if relevant chunks pass the check
    context_blocks = []
    for i, result in enumerate(search_results):
        context_blocks.append(f"Source {i+1}:\n{result['content']}")
    
    context_string = "\n\n".join(context_blocks)

    # 5. Strict System Prompt (ensuring LLM doesn't hallucinate or go off-topic)
    system_prompt = (
        "You are a strict context-aware AI support assistant. "
        "You must answer the user's question using ONLY the provided context below. "
        "Do NOT use any outside knowledge. Do NOT answer general queries, jokes, or chit-chat. "
        "If the answer cannot be strictly found in the context, reply with: "
        "'I cannot find the answer in the provided documents.'"
    )
    
    user_prompt = f"Context:\n{context_string}\n\nUser Question: {payload.question}"

    # 6. Call local Ollama model
    response = ollama.chat(
        model="llama3.1", # or "phi3" depending on what you configured earlier
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )

    answer_text = response["message"]["content"]

    return ChatResponse(answer=answer_text, results=search_results)