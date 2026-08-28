from fastapi import APIRouter, Depends, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.document import Document
from app.schemas.documents import DocumentResponse

router = APIRouter(prefix="/documents", tags=["documents"])

@router.get("/", response_model=list[DocumentResponse])
async def list_documents(db: AsyncSession = Depends(get_db)):
       result = await db.scalars(select(Document))
       return result.all()

@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
):
    # Read the file's bytes to compute size and handle contents
    content = await file.read()
    file_size = len(content)

    # Create the Document database model instance
    db_document = Document(
        filename=file.filename or "unknown",
        content_type=file.content_type or "application/octet-stream",
        size_bytes=file_size,
        status="processing",
        chunk_count=0,
    )

    # Add to session, commit, and refresh to fetch auto-generated fields (id, created_at)
    db.add(db_document)
    await db.commit()
    await db.refresh(db_document)

    return db_document