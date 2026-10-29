import re

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator, Field
from starlette import status


class AuthRequestSchema(BaseModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(from_attributes=True)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):

        errors = []

        if not 8 <= len(value) <= 32:
            errors.append('Пароль должен содержать от 8 до 32 символоы')
        if not re.search(r"[A-ZА-Я]", value):
            errors.append('Пароль должен содержать хотя бы одну заглавную букву')
        if not re.search(r"\d", value):
            errors.append('Пароль должен содержать хотя бы одну цифру')
        if not re.search(r"[!@#$%^&*()_+=\[{\]};:<>|./?,-]", value):
            errors.append('Пароль должен содержать хотя бы один спецсимвол (!@#$%^&*()_+=:<>|./?,-)')


        if errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    'message': 'Пароль не прошел валидацию',
                    'errors': errors
                }
            )
        else:
            return value




class AuthResponseSchema(BaseModel):
    id: int
    email: EmailStr
    role: str

    model_config = ConfigDict(from_attributes=True)


class TokenRequestSchema(BaseModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(from_attributes=True)

class TokenResponseSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(from_attributes=True)
