from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from src.core.config import settings

db_url = settings.DATABASE_URL

engine = create_async_engine(
    db_url,
    connect_args={"check_same_thread": False}
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)

# 3. Base Model 
class Base(DeclarativeBase):
    pass

# 4. Async Dependency 
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
