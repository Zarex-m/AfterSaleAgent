from app.schemas.document import DocumentResponse
from app.db.models.document import Document
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


async def list_documents(db: AsyncSession)->list[Document]:
    result=await db.execute(select(Document).order_by(Document.created_at.desc()))
    return result.scalars().all()

async def get_document_by_id(db: AsyncSession, document_id: int) -> Document | None:
    result=await db.execute(select(Document).where(Document.id == document_id))
    return result.scalar_one_or_none()

async def create_document_record(
    db:AsyncSession,
    title:str,
    file_path:str,
    uploaded_by:int
)->Document:
    new_doc=Document(
        title=title,
        file_path=file_path,
        uploaded_by=uploaded_by,
    )
    db.add(new_doc)
    await db.commit()
    await db.refresh(new_doc)
    return new_doc