from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field, ConfigDict, field_validator, StringConstraints, model_validator


ProductName = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)
]
ProductDescription = Annotated[
    str, StringConstraints(strip_whitespace=True,max_length=3000)
]
ProductCategoryId = Annotated[
    int, Field(gt=0, strict=True),
]
ProductPrice = Annotated[
    Decimal, Field(gt=0)
]
ProductStock = Annotated[
    int, Field(ge=0, strict=True)
]


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
