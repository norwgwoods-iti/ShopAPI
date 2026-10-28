from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import DeclarativeBase
from starlette import status

# from shopapi.models.user import UserModel


class Base(DeclarativeBase):
    pass



