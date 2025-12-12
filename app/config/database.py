from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config.settings import get_settings 
from sqlmodel import SQLModel

settings = get_settings()

class Base(DeclarativeBase): 
    pass

engine = create_async_engine(
    settings.DATABASE_URL, 
    echo = settings.APP_DEBUG, 
    future = True
)

AsyncSessionLocal = async_sessionmaker(
    bind = engine, 
    class_ = AsyncSession, 
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_db() -> AsyncSession: 
    async with AsyncSessionLocal as session: 
        try:
            yield session 
            await session.commit()
        except Exception: 
            await session.rollback()
            raise
        finally: 
            await session.close()

async def init_db(): 
    async with engine.begin() as conn: 
        await conn.run_sync(SQLModel.metadata.create_all)


