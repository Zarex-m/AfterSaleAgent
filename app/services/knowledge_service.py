import re
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.document import Document, DocumentChunk, DocumentStatus
from app.services.document_service import get_document_by_id

#读取文本文件内容
def read_text_file(file_path:str)->str:
    path=Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if path.suffix.lower() not in {".txt", ".md"}:
        raise ValueError("Unsupported file type. Only .txt and .md are allowed.")
    
    return path.read_text(encoding="utf-8")

#清洗文本内容，去除多余的空白和特殊字符
def clean_text(text: str) -> str:
    if not text:
        return ""
    # 重新按 UTF-8 编码/解码，忽略无法识别的非法字符
    text = text.encode("utf-8", errors="ignore").decode("utf-8")
    
    
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\u00a0", " ")
    text = text.replace("\t", " ")

    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ ]{2,}", " ", text)

    return text.strip()

#将文本分割成适合处理的小块，默认每块800字符，重叠150字符
def split_text(text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        length_function=len,
        is_separator_regex=False,
        separators=[
            "\n\n",
            "\n",
            " ",
            "。",
            "，",
            "、",
            ".",
            ",",
            "",
        ],
    )

    return [chunk.strip() for chunk in splitter.split_text(text) if chunk.strip()]

async def delete_chunks_by_document_id(
    db: AsyncSession,
    document_id: int,
) -> None:
    await db.execute(
        delete(DocumentChunk).where(DocumentChunk.document_id == document_id)
    )
    
async def ingest_document(
    db: AsyncSession,
    document_id: int,
) -> dict:
    document = await get_document_by_id(db, document_id)
    if document is None:
        raise ValueError("DOCUMENT_NOT_FOUND")

    if not document.file_path:
        raise ValueError("DOCUMENT_FILE_MISSING")

    try:
        document.status = DocumentStatus.PROCESSING.value
        await db.flush()

        raw_text = read_text_file(document.file_path)
        cleaned_text = clean_text(raw_text)
        chunks = split_text(cleaned_text)

        await delete_chunks_by_document_id(db, document.id)

        for index, chunk in enumerate(chunks):
            db.add(
                DocumentChunk(
                    document_id=document.id,
                    content=chunk,
                    chunk_index=index,
                    metadata_json={
                        "title": document.title,
                        "source_type": document.source_type,
                        "file_path": document.file_path,
                    },
                )
            )

        document.status = DocumentStatus.READY.value
        await db.commit()
        await db.refresh(document)

        return {
            "document_id": document.id,
            "status": document.status,
            "chunk_count": len(chunks),
        }

    except Exception:
        document.status = DocumentStatus.FAILED.value
        await db.commit()
        raise

#把用户的查询拆成关键词
def tokenize_query(query: str) -> list[str]:
    normalized = query.strip().lower()
    if not normalized:
        return []

    tokens = re.split(r"[\s,，。！？!?.；;：:、]+", normalized)
    return [token for token in tokens if token]

#计算查询与文本块的相关度得分，完全匹配得2分，包含关键词得1分
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

#从数据库所有切片中，找出最相关的前K个切片返回给用户
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
