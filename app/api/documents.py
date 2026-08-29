from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db, async_session_maker
from app.models.document import Document
from app.schemas.documents import DocumentResponse
from app.services.document_processor import extract_text, recursive_chunk_text
from app.services.embeddings import embed_texts
from app.services.vector_store import ensure_collection, upsert_chunks
from fastapi import HTTPException
from app.services.vector_store import delete_document_vectors

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/", response_model=list[DocumentResponse])
async def list_documents(db: AsyncSession = Depends(get_db)):
    result = await db.scalars(select(Document))
    return result.all()


async def process_document(document_id: str, filename: str, content: bytes) -> None:
    """Runs in the background, after the upload response has already been sent."""
    async with async_session_maker() as db:
        document = await db.get(Document, document_id)
        try:
            text = extract_text(filename, content)
            chunks = recursive_chunk_text(text)
            embeddings = embed_texts(chunks)
            ensure_collection()
            upsert_chunks(document_id, chunks, embeddings)
            document.chunk_count = len(chunks)
            document.status = "ready"
        except Exception as e:
            document.status = "failed"
            document.error_message = str(e)[:500]
        await db.commit()


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    content = await file.read()

    db_document = Document(
        filename=file.filename or "unknown",
        content_type=file.content_type or "application/octet-stream",
        size_bytes=len(content),
        status="processing",
        chunk_count=0,
    )
    db.add(db_document)
    await db.commit()
    await db.refresh(db_document)

    background_tasks.add_task(process_document, str(db_document.id), db_document.filename, content)
    return db_document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: str, db: AsyncSession = Depends(get_db)):
    document = await db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    delete_document_vectors(document_id)
    await db.delete(document)
    await db.commit()