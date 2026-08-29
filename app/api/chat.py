import ollama
from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.embeddings import embed_texts 
from app.services.vector_store import search_similar_chunks
from app.guardrails.pii_detector import detect_pii, PII_PATTERNS
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
async def chat(payload: ChatRequest):
    # 1. Redact PII from the incoming question
    safe_question = redact_pii(payload.question)
    
    # Optional verification print to check redaction in terminal
    print(f"Original Question: {payload.question}")
    print(f"Safe Question (Redacted): {safe_question}")
    
    # 2. Embed the safe, redacted question
    query_vector = embed_texts([safe_question])[0]
    
    # 3. Search for similar chunks with score threshold
    results = search_similar_chunks(query_vector=query_vector, top_k=3, score_threshold=0.3)
    
    # 4. Refuse if no relevant context found
    if not results:
        return ChatResponse(
            answer="I don't have enough information in the knowledge base to answer that question.",
            results=[]
        )
    
    # 5. Build context string
    context = "\n\n".join(r["content"] for r in results)
    
    # 6. Generate answer using the traced helper function
    answer_text = generate_answer(question=safe_question, context=context)

    return ChatResponse(answer=answer_text, results=results)