from pydantic import ConfigDict
from shopapi.schemas.product import ProductResponseSchema, ProductListResponseSchema

class StrictProductResponse(ProductResponseSchema):
    model_config = ConfigDict(from_attributes=True, extra='forbid')

class StrictProductListResponse(ProductListResponseSchema):
    model_config = ConfigDict(from_attributes=True, extra='forbid')