import ollama
from fastapi import APIRouter, Request
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.embeddings import embed_texts 
from app.services.vector_store import search_similar_chunks, search_semantic_cache, store_semantic_cache
from app.guardrails.pii_detector import PII_PATTERNS
from app.core.limiter import limiter
from langsmith import traceable

def redact_pii(text: str) -> str:
    redacted = text
    for label, pattern in PII_PATTERNS.items():
        redacted = pattern.sub(f"[REDACTED_{label.upper()}]", redacted)
    return redacted

router = APIRouter(prefix="/chat", tags=["chat"])

@traceable(name="generate_answer")
def generate_answer(question: str, context: str) -> str:
    system_prompt = (
        "You are a helpful AI assistant. Answer the user's question "
        "using ONLY the provided context below. Do not use outside knowledge."
    )
    user_prompt = f"Context:\n{context}\n\nUser Question: {question}"

    response = ollama.chat(
        model="llama3.1",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )
    return response["message"]["content"]

@router.post("/", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat(request: Request, payload: ChatRequest):
    # 1. Redact PII from the incoming question
    safe_question = redact_pii(payload.question)
    
    # 2. Embed the safe question first (needed for both semantic cache lookup and RAG search)
    query_vector = embed_texts([safe_question])[0]
    
    # 3. Check Semantic Cache in Qdrant (Threshold >= 0.95 for high semantic overlap)
    cached_answer = search_semantic_cache(query_vector, score_threshold=0.95)
    if cached_answer:
        print("Semantic Cache hit! Returning response from Qdrant cache.")
        return ChatResponse(answer=cached_answer, results=[])

    # 4. Search for similar document chunks if cache misses
    results = search_similar_chunks(query_vector=query_vector, top_k=3, score_threshold=0.3)
    
    # 5. Refuse if no relevant context found
    if not results:
        refusal_msg = "I don't have enough information in the knowledge base to answer that question."
        return ChatResponse(answer=refusal_msg, results=[])
    
    # 6. Build context string and generate answer via LLM
    context = "\n\n".join(r["content"] for r in results)
    answer_text = generate_answer(question=safe_question, context=context)

    # 7. Store the new question vector and answer in the semantic cache
    store_semantic_cache(safe_question, query_vector, answer_text)

    return ChatResponse(answer=answer_text, results=results)