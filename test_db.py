from pathlib import Path
from app.services.document_processor import extract_text

def test_extraction():
    # 1. Create a dummy text file temporarily on disk
    test_file_path = Path("sample.txt")
    test_content = "Hello! This is a test document for our RAG pipeline."
    test_file_path.write_text(test_content, encoding="utf-8")

    try:
        # 2. Read it back as bytes (mimicking an upload)
        file_bytes = test_file_path.read_bytes()
        
        # 3. Call the extract_text function
        extracted = extract_text("sample.txt", file_bytes)
        
        print(f"Extraction successful!\nResult: {extracted}")
    finally:
        # Cleanup the test file
        if test_file_path.exists():
            test_file_path.unlink()

if __name__ == "__main__":
    test_extraction()