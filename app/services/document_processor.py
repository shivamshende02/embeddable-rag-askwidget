import io
from pypdf import PdfReader

def extract_text(filename: str, content: bytes) -> str:
       lower = filename.lower()
       if lower.endswith(".txt"):
           return content.decode("utf-8", errors="ignore")
       if lower.endswith(".pdf"):
           reader = PdfReader(io.BytesIO(content))
           pages_text = []
           for page in reader.pages:
               pages_text.append(page.extract_text() or "")
           return "\n\n".join(pages_text)
       raise ValueError(f"Unsupported file type: {filename}")