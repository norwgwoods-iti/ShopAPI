from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from starlette import status

from shopapi.core.config import Settings, settings
from shopapi.core.security import hash_password, verify_password, create_access_token
from shopapi.db.session import SessionDep
from shopapi.models.user import UserModel
from shopapi.schemas.auth import AuthResponseSchema, AuthRequestSchema, TokenRequestSchema, TokenResponseSchema

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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        session: SessionDep
) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    query = select(UserModel).where(UserModel.email == email)
    result = await session.execute(query)
    user = result.scalars().first()

    if user is None:
        raise credentials_exception
    return user


@router.post(
    "/register",
    response_model=AuthResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
        session: SessionDep,
        user: AuthRequestSchema,
):

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



@router.post(
    "/login",
    response_model=TokenResponseSchema,
)
async def auth_login(
        session: SessionDep,
        # credentials: TokenRequestSchema,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    query = select(UserModel).where(UserModel.email == form_data.username)
    result = await session.execute(query)
    user = result.scalars().first()


    if not user or not verify_password(plain_password=form_data.password, hashed_password=user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub" : user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get(
    "/me",
    response_model=AuthResponseSchema
)
async def auth_me(
        current_user: Annotated[UserModel, Depends(get_current_user)],
):
    return current_user

"""
Регистрация по email и паролю.
Вход и получение JWT access token.
Хеширование паролей.
Роли user и admin.
Запрет доступа к защищённым ресурсам без валидного токена.
Запрет обычному пользователю изменять чужие данные."""