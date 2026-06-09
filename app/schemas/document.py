from datetime import datetime
from pydantic import BaseModel

class DocumentResponse(BaseModel):
    id: int
    title: str
    source_type: str
    file_path: str | None
    status:str
    uploaded_by:int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}