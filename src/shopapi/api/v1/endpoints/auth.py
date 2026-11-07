from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from starlette import status

from shopapi.core.dependencies import CurrentUserDep
from shopapi.core.security import hash_password, verify_password, create_access_token
from shopapi.core.dependencies import SessionDep
from shopapi.models.enums import UserRole
from shopapi.models.user import UserModel
from shopapi.schemas.auth import AuthResponseSchema, AuthRequestSchema, TokenResponseSchema

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

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
        role=UserRole.USER,
    )

    session.add(new_user)

    try:
        await session.commit()
        await session.refresh(new_user)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Email already registered"
            }
        )

    return new_user



@router.post(
    "/login",
    response_model=TokenResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def auth_login(
        session: SessionDep,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    query = select(UserModel).where(UserModel.email == form_data.username)
    result = await session.execute(query)
    user = result.scalars().first()

    if not user or not verify_password(plain_password=form_data.password, hashed_password=user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
            detail={
                "message": "Incorrect username or password",
            }
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
        current_user: CurrentUserDep,
):
    return current_user