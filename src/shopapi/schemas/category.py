from pydantic import BaseModel, ConfigDict


class CategoryResponseSchema(BaseModel):
    id:int
    name:str
    slug:str

    model_config = ConfigDict(from_attributes=True)

class ProductListResponseSchema(BaseModel):
    total: int
    page:int
    page_size: int
    items:list[CategoryResponseSchema]

    model_config = ConfigDict(from_attributes=True)

class CategoryCreateSchema(BaseModel):
    name: str
    slug: str

    model_config = ConfigDict(from_attributes=True)

class CategoryUpdateSchema(BaseModel):
    name: str | None = None
    slug: str | None = None

    model_config = ConfigDict(from_attributes=True)