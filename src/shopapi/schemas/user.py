from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserSchema(BaseModel):
    id: int
    email: str
    password_hash: str
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


