from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.document import Document, DocumentChunk


async def list_documents(db: AsyncSession) -> list[Document]:
    result = await db.execute(select(Document).order_by(Document.created_at.desc()))
    return list(result.scalars().all())


async def get_document_by_id(db: AsyncSession, document_id: int) -> Document | None:
    result = await db.execute(select(Document).where(Document.id == document_id))
    return result.scalar_one_or_none()


async def create_document_record(
    db: AsyncSession,
    title: str,
    file_path: str,
    uploaded_by: int,
) -> Document:
    document = Document(
        title=title,
        file_path=file_path,
        uploaded_by=uploaded_by,
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    return document


async def delete_chunks_by_document_id(db: AsyncSession, document_id: int) -> None:
    await db.execute(
        delete(DocumentChunk).where(DocumentChunk.document_id == document_id)
    )


async def create_document_chunks(
    db: AsyncSession,
    chunks: list[DocumentChunk],
) -> None:
    db.add_all(chunks)


async def list_document_chunks(db: AsyncSession) -> list[DocumentChunk]:
    result = await db.execute(select(DocumentChunk))
    return list(result.scalars().all())
