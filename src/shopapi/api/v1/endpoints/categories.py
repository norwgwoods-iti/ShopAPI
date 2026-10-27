from typing import Literal

from fastapi import APIRouter, Query
from sqlalchemy import select
from starlette import status
from starlette.responses import Response

from shopapi.db.session import SessionDep
from shopapi.models import ProductModel
from shopapi.models.category import CategoryModel
from shopapi.schemas.category import CategoryResponseSchema

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)

@router.get("/", response_model=CategoryResponseSchema)
async def get_categories(
        session: SessionDep,
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100),
        search: str | None = Query(default=None, min_length=1, max_length=100),
        sort_by: Literal["name", "slug"] = "name",
        order: Literal["asc", "desc"] = "desc",

):

    query = (
        select(CategoryModel)
        .where(CategoryModel.id.is_(not None))
    )

    if search is not None:
        query = query.where(
            CategoryModel.name.ilike(f"%{search.split()}%")
        )

    sort_column = {
        "name": CategoryModel.name,
        "slug": CategoryModel.slug,
    }[sort_by]

    if order == "asc":
        query = query.order_by(sort_column.asc(), ProductModel.id.asc())
    else:
        query = query.order_by(sort_column.desc(), ProductModel.id.desc())


    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await session.scalars(query)

    # categories = await session.scalars(select(CategoryModel).order_by(CategoryModel.id))

    return result.all()



@router.get("/{category_id}", response_model=CategoryResponseSchema)
async def get_category(
        session: SessionDep,
        category_id: int
):

    category = await session.get(CategoryModel, category_id)

    if not category:
        return Response(
            status_code=status.HTTP_404_NOT_FOUND,
            content=f"Category {category_id} not found"
        )

    return category







# @router.post("/")
# async def create_categories(session: SessionDep, category: CategoryResponseSchema):
#     new_category = CategoryModel(
#         id=category.id,
#         name=category.name,
#         slug=category.slug,
#     )
#     session.add(new_category)
#
#     try:
#         await session.commit()
#     except IntegrityError:
#         session.rollback()
#         raise HTTPException(
#             status_code=409,
#             detail=f"Category {category.name} already exists"
#         )
#     return {
#         "id": new_category.id,
#         "name": new_category.name,
#         "slug": new_category.slug,
#     }