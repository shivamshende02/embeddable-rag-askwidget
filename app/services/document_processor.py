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

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 150) -> list[str]:
       normalized = " ".join(text.split())  # collapse whitespace/newlines
       if not normalized:
           return []

       chunks = []
       start = 0
       while start < len(normalized):
           end = min(start + chunk_size, len(normalized))
           chunks.append(normalized[start:end])
           if end == len(normalized):
               break
           start = end - overlap
       return chunks

def recursive_chunk_text(
    text: str,
    chunk_size: int = 1000,
    separators: list[str] | None = None,
) -> list[str]:
    if separators is None:
        separators = ["\n\n", "\n", ". ", " ", ""]

    # Base case: if text is empty or small enough, return it as a single chunk
    if len(text) <= chunk_size:
        return [text] if text.strip() else []

    current_separator = ""
    next_separators = []

    # Find the first separator that exists in the text
    for i, sep in enumerate(separators):
        if sep == "":
            current_separator = sep
            next_separators = separators[i + 1:]
            break
        if sep in text:
            current_separator = sep
            next_separators = separators[i + 1:]
            break

    # Split the text by the chosen separator
    if current_separator:
        splits = text.split(current_separator)
    else:
        splits = list(text)

    good_splits = []
    separator_to_use = current_separator

    for s in splits:
        if len(s) <= chunk_size:
            good_splits.append(s)
        else:
            # If a single split is still too large, recursively break it down using smaller separators
            if good_splits:
                merged = separator_to_use.join(good_splits)
                # We handle merging/splitting recursively or yield chunks
                # For simplicity, let's process nested chunks recursively
                pass
            
            sub_chunks = recursive_chunk_text(s, chunk_size, next_separators)
            good_splits.extend(sub_chunks)

    # Now merge small splits back together up to chunk_size limit
    chunks = []
    current_chunk = []
    current_length = 0

    for part in good_splits:
        part_len = len(part) + len(separator_to_use) if current_chunk else len(part)
        if current_length + part_len <= chunk_size:
            current_chunk.append(part)
            current_length += part_len
        else:
            if current_chunk:
                chunks.append(separator_to_use.join(current_chunk))
            current_chunk = [part]
            current_length = len(part)

    if current_chunk:
        chunks.append(separator_to_use.join(current_chunk))

    return [c.strip() for c in chunks if c.strip()]