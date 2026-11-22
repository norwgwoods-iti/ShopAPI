from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
def empty_to_none(value):
    if isinstance(value, str) and not value.strip():
        return None
    return value


class ProductCreateSchema(BaseModel):
    name: ProductName
    description: ProductDescription | None = None
    category_id: ProductCategoryId
    price: ProductPrice
    stock: ProductStock
    is_active: bool = True

    _empty_to_none = field_validator(
        "description", mode="before"
    )(empty_to_none)


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
    is_active: bool = True

class ProductResponseCreateSchema(ProductCreateSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)

class ProductUpdateSchema(BaseModel):
    name: ProductName | None = None
    description: ProductDescription | None = None
    category_id: ProductCategoryId | None = None
    price: ProductPrice | None = None
    stock: ProductStock | None = None

    _empty_to_none = field_validator(
        "description", mode="before"
    )(empty_to_none)

    @model_validator(mode="before")
    @classmethod
    def validate_null_fields(cls, data):
        if not isinstance(data, dict):
            return data

        nullable_fields = {"description"}

        for field, value in data.items():
            if field not in nullable_fields and value is None:
                raise ValueError(f'"{field}" cannot be null')

        return data


class ProductStatusUpdateSchema(BaseModel):
    is_active: bool

class ProductStatusUpdateResponseSchema(BaseModel):
    id: int
    name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
