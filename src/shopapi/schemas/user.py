from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserSchema(BaseModel):
    id: int
    email: str
    password_hash: str
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserCreateSchema(BaseModel):
    email: str
    password: str

    model_config = ConfigDict(from_attributes=True)


class UserResponseSchema(BaseModel):
    id: int
    email: str
    role: str

    model_config = ConfigDict(from_attributes=True)