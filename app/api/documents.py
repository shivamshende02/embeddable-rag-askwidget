from fastapi import APIRouter, Depends
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