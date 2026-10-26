import os

from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from shopapi.db.base import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")


engine = create_async_engine(DATABASE_URL, echo=True)

new_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with new_session() as session:
        yield session



async def create_table():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code = 500,
            detail="Create table failed.",
        )
    return {"status": "ok"}

#
# from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
# from shopapi.core.config import settings
#
#
# engine = create_async_engine(
#     settings.database_url,
#     echo=False,
#     pool_pre_ping=True,
# )
#
# async_session_factory = async_sessionmaker(
#     bind=engine,
#     class_=AsyncSession,
#     expire_on_commit=False,
# )
#
#
# async def get_db():
#     async with async_session_factory() as session:
#         yield session
