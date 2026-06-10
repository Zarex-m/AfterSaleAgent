from app.schemas.document import DocumentResponse
from app.db.models.document import Document
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import re
from app.db.models.document import DocumentChunk

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

def tokenize_query(query: str) -> list[str]:
    normalized = query.strip().lower()
    if not normalized:
        return []

    tokens = re.split(r"[\s,，。！？!?.；;：:、]+", normalized)
    return [token for token in tokens if token]


def calculate_keyword_score(query: str, content: str, tokens: list[str]) -> float:
    normalized_query = query.strip().lower()
    normalized_content = content.lower()

    score = 0.0

    if normalized_query and normalized_query in normalized_content:
        score += 2.0

    for token in tokens:
        if token in normalized_content:
            score += 1.0

    return score


async def search_policy_chunks(
    db: AsyncSession,
    query: str,
    top_k: int = 5,
) -> list[dict]:
    tokens = tokenize_query(query)

    result = await db.execute(select(DocumentChunk))
    chunks = result.scalars().all()

    scored_results = []
    for chunk in chunks:
        score = calculate_keyword_score(query, chunk.content, tokens)
        if score <= 0:
            continue

        scored_results.append(
            {
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "score": score,
                "metadata": chunk.metadata_json,
            }
        )

    scored_results.sort(key=lambda item: item["score"], reverse=True)
    return scored_results[:top_k]