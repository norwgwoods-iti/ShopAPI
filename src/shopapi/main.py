import contextlib

from uvicorn import lifespan

from shopapi.api.v1.router import main_router
from fastapi import FastAPI, HTTPException
from sqlalchemy import text, select
from sqlalchemy.exc import SQLAlchemyError

from shopapi.db.base import Base
from shopapi.db.session import engine, create_table


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):

    await create_table()

    yield

    await engine.dispose()


app = FastAPI(
    title="Shop API",
    lifespan=lifespan
)

app.include_router(main_router)

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


