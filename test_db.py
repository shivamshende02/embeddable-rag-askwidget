from app.services.document_processor import recursive_chunk_text

def test_recursive():
    sample_text = (
        "First paragraph goes here. It has multiple sentences to check splitting.\n\n"
        "Second paragraph is slightly longer and contains technical details about RAG pipelines, "
        "embeddings, vector databases, and semantic text chunking strategies."
    )
    
    chunks = recursive_chunk_text(sample_text, chunk_size=100)
    print(f"Total chunks: {len(chunks)}\n")
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i+1} ({len(chunk)} chars):\n{chunk}\n")

if __name__ == "__main__":
    test_recursive()