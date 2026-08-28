from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime

class DocumentResponse(BaseModel):
       model_config = ConfigDict(from_attributes=True)

       id: uuid.UUID
       filename: str
       content_type: str
       size_bytes: int
       status: str
       chunk_count: int
       error_message: str | None
       created_at: datetime