from pydantic import BaseModel


class CategoryResponseSchema(BaseModel):
    id:int
    name:str
    slug:str

