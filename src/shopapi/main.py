import shopapi.models
import contextlib

from shopapi.api.v1.router import main_router
from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from shopapi.db.base import Base
from shopapi.db.session import engine


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    print("TABLES:", list(Base.metadata.tables.keys()))  # ← временно
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(
    title="Shop API",
    lifespan=lifespan
)

app.include_router(main_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code = 503,
            detail="Database connection failed.",
        ) from exc
    return {"status": "ok"}



#
# @app.post("/create_table")
# async def create_table():
#     try:
#         async with engine.begin() as conn:
#             await conn.run_sync(Base.metadata.create_all)
#     except SQLAlchemyError as exc:
#         raise HTTPException(
#             status_code = 500,
#             detail="Create table failed.",
#         )
#     return {"status": "ok"}