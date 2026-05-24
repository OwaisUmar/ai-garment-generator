from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config.settings import settings

# Async engine (FastAPI)
async_engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(bind=async_engine, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as db:
        yield db


# Sync engine (Celery)
sync_database_url = settings.DATABASE_URL.replace("+asyncpg", "",)
sync_engine = create_engine(sync_database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=sync_engine, autoflush=False, expire_on_commit=False)

from sqlalchemy.orm import DeclarativeBase, sessionmaker

class Base(DeclarativeBase):
    pass