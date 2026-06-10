from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.schemas.knowledge import KnowledgeSearchRequest, KnowledgeSearchResponse
from app.services.knowledge_service import search_policy_chunks

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.post("/search", response_model=KnowledgeSearchResponse)
async def search_knowledge(
    data: KnowledgeSearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> KnowledgeSearchResponse:
    results = await search_policy_chunks(
        db=db,
        query=data.query,
        top_k=data.top_k,
    )

    return KnowledgeSearchResponse(
        query=data.query,
        results=results,
    )