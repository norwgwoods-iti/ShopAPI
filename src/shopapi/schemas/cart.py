from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CartItemResponseSchema(BaseModel):
    id: int # id записи
    product_id: int #
    name: str
    unit_price: Decimal
    quantity: int
    subtotal: Decimal

    model_config = ConfigDict(from_attributes=True)

class CartListResponseSchema(BaseModel):
    total_amount: Decimal
    items: list[CartItemResponseSchema]

    model_config = ConfigDict(from_attributes=True)

class CartItemCreateSchema(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(default=1, gt=0)

class CartItemUpdateSchema(BaseModel):
    quantity: int = Field(gt=0)
