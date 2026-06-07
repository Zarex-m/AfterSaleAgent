from fastapi import APIRouter,Depends
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check()->dict[str,str]:
    return {"status": "ok"}

@router.get("/health/db")
async def health_check_db(
    db:AsyncSession=Depends(get_db)
)->dict[str,str]:
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok","database": "connected"}
    except Exception as e:
        return {"status": "error", "details": str(e)}