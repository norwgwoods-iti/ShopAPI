from pydantic import BaseModel, ConfigDict

class AuthRequestSchema(BaseModel):
    email: str
    password: str

    model_config = ConfigDict(from_attributes=True)


class AuthResponseSchema(BaseModel):
    id: int
    email: str
    role: str

    model_config = ConfigDict(from_attributes=True)


class TokenRequestSchema(BaseModel):
    email: str
    password: str

    model_config = ConfigDict(from_attributes=True)

class TokenResponseSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(from_attributes=True)
