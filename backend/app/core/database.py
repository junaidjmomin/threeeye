import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.core.config import settings

_is_pooler = "pooler.supabase" in settings.DATABASE_URL
_is_testing = os.getenv("TESTING", "false").lower() == "true"

if _is_testing:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        poolclass=NullPool,
    )
else:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        pool_size=20,
        max_overflow=10,
        # Supabase connection pooler doesn't support prepared statements
        **( {"connect_args": {"statement_cache_size": 0, "prepared_statement_cache_size": 0}}
            if _is_pooler else {}),
    )

async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
