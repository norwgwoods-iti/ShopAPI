from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict




# class ProductAddSchema(BaseModel):
#     category_id: int
#     name: str
#     description : str | None
#     price: Decimal
#     stock: int
#
#     model_config = ConfigDict(from_attributes=True)

# class ProductResponseSchema(BaseModel):
#     id: int
#     is_active: bool
#     created_at: datetime
#
#     model_config = ConfigDict(from_attributes=True)

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
