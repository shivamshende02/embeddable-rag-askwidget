import ollama
from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.embeddings import embed_texts 
from app.services.vector_store import search_similar_chunks

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    # 1. Embed the user's question using the embedding service
    question_embeddings = embed_texts([payload.question])
    query_vector = question_embeddings[0]
    
    # 2. Retrieve top similar chunks from Qdrant vector store
    search_results = search_similar_chunks(query_vector=query_vector, top_k=3)
    
    # 3. Build context string from retrieved chunks
    context_blocks = []
    for i, result in enumerate(search_results):
        context_blocks.append(f"Source {i+1}:\n{result['content']}")
    
    context_string = "\n\n".join(context_blocks) if context_blocks else "No relevant context found."

    # 4. Construct prompts combining context and question
    system_prompt = (
        "You are a helpful, context-aware AI support assistant. Answer the user's question "
        "using ONLY the provided context below. If the answer cannot be found in the context, "
        "politely state that you do not know based on the available information."
    )
    
    user_prompt = f"Context:\n{context_string}\n\nUser Question: {payload.question}"

    # 5. Call local Ollama model
    response = ollama.chat(
        model="llama3.1",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )

    # 6. Extract generated answer text and return with sources
    answer_text = response["message"]["content"]

    return ChatResponse(answer=answer_text, results=search_results)