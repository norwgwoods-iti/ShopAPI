from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shopapi.db.session import get_session
from shopapi.models.enums import UserRole
from shopapi.models.user import UserModel
from shopapi.core.config import settings


SessionDep = Annotated[AsyncSession, Depends(get_session)]


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        session: SessionDep
) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers={"WWW-Authenticate": "Bearer"},
        detail={
            "message": "Could not validate token"
        },
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
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception
    return user


CurrentUserDep = Annotated[UserModel, Depends(get_current_user)]


async def get_current_admin(
        current_user: Annotated[UserModel, Depends(get_current_user)]
) -> UserModel:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Admin access required"
            },
        )
    return current_user


CurrentAdminDep = Annotated[UserModel, Depends(get_current_admin)]