from app.db.models.document import Document
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import document_repository

async def list_documents(db: AsyncSession)->list[Document]:
    return await document_repository.list_documents(db)

async def get_document_by_id(db: AsyncSession, document_id: int) -> Document | None:
    return await document_repository.get_document_by_id(db, document_id)

async def create_document_record(
    db:AsyncSession,
    title:str,
    file_path:str,
    uploaded_by:int
)->Document:
    return await document_repository.create_document_record(
        db=db,
        title=title,
        file_path=file_path,
        uploaded_by=uploaded_by,
    )
