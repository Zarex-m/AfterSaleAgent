from app.core.config import settings

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine,async_sessionmaker
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

engine=create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)
    
async def get_db()->AsyncGenerator[AsyncSession,None]:
    async with SessionLocal() as session:
        yield session #这里的yield相当于return session