from pydantic import BaseModel, Field


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    top_k: int = Field(default=5, ge=1, le=20)


class KnowledgeSearchResult(BaseModel):
    chunk_id: int
    document_id: int
    chunk_index: int
    content: str
    score: float
    metadata: dict | None = None


class KnowledgeSearchResponse(BaseModel):
    query: str
    results: list[KnowledgeSearchResult]