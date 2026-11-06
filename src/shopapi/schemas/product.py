from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict

class ProductResponseSchema(BaseModel):
    id: int
    category_id: int
    name: str
    description: str | None
    price: Decimal
    stock: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ProductListResponseSchema(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[ProductResponseSchema]

    model_config = ConfigDict(from_attributes=True)

class ProductCreateSchema(BaseModel):
    name: str
    description: str | None = Field(default="Описание(необязательное поле)")
    category_id: int
    price: Decimal
    stock: int

class ProductResponseCreateSchema(ProductCreateSchema):
    id: int
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)

class ProductUpdateSchema(BaseModel):
    name: str | None = None
    description: str | None = None
    category_id: int | None = None
    price: Decimal | None = None
    stock: int  | None = None


class ProductStatusUpdateSchema(BaseModel):
    is_active: bool

class ProductStatusUpdateResponseSchema(BaseModel):
    id: int
    name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
