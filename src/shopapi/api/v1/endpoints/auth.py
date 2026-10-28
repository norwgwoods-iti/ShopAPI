# import os
# from datetime import timedelta, datetime, timezone
# from idlelib import query
# from typing import Annotated
#
# import jwt
# from argon2 import PasswordHasher
from fastapi import FastAPI, APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pwdlib import PasswordHash
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.testing.pickleable import User
from starlette import status
from dotenv import load_dotenv

from shopapi.core.security import hash_password
# from shopapi.db.base import assertion_email_register
from shopapi.db.session import SessionDep
from shopapi.models.user import UserModel
from shopapi.schemas.user import UserResponseSchema, UserCreateSchema

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


# async def assertion_email_register(user, session):
#     query = select(UserModel).where(UserModel.email == user.email)
#     result = await session.execute(query)
#     existing_user = result.scalars().first()
#     if existing_user:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Email already registered",
#         )
#     return


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")



@router.post(
    "/register",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
        session: SessionDep,
        user: UserCreateSchema,
):
    # await assertion_email_register(user, session)

    hashed_pwd = hash_password(user.password)

    new_user = UserModel(
        email=user.email,
        password_hash=hashed_pwd,
    )

    session.add(new_user)

    try:
        await session.commit()
        await session.refresh(new_user)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    return new_user


# @router.post("/login")
# async def auth_login():
#     OAuth2 = "password from"
#     ...

    """
    username = email
    password = form data

    Authorization: Bearer <jwt>

    {
        "access_token": "<jwt>",
        "token_type": "bearer"
    }
    """



# @router.get("/auth/me")
# async def auth_me():
#     ...


"""
Регистрация по email и паролю.
Вход и получение JWT access token.
Хеширование паролей.
Роли user и admin.
Запрет доступа к защищённым ресурсам без валидного токена.
Запрет обычному пользователю изменять чужие данные."""