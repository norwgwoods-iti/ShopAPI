from typing import Literal, Annotated

from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from starlette import status
from starlette.responses import Response

from shopapi.api.v1.endpoints.auth import get_current_user
from shopapi.db.session import SessionDep
from shopapi.models import UserModel
from shopapi.models.category import CategoryModel
from shopapi.schemas.category import CategoryResponseSchema, ProductListResponseSchema, CategoryCreateSchema

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)

@router.get("/", response_model=ProductListResponseSchema)
async def get_categories(
        session: SessionDep,
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100),
        search: str | None = Query(default=None, min_length=1, max_length=100),
        sort_by: Literal["name", "slug"] = "name",
        order: Literal["asc", "desc"] = "asc",

):

    query = (
        select(CategoryModel)
        # .where(CategoryModel.id.is_(not None))
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
        query = query.order_by(sort_column.asc(), CategoryModel.id.asc())
    else:
        query = query.order_by(sort_column.desc(), CategoryModel.id.desc())

    count_query = select(func.count()).select_from(
        query.order_by(None).subquery()
    )
    total = await session.scalar(count_query)

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await session.scalars(query)
    items = result.all()



    return ProductListResponseSchema(
        total=total or 0,
        page=page,
        page_size=page_size,
        items=items,
    )



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



@router.post(
    path="/",
    response_model=CategoryResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
        session: SessionDep,
        form_data: CategoryCreateSchema,
        current_user: Annotated[UserModel, Depends(get_current_user)]
):
    query = select(CategoryModel).where(CategoryModel.name == form_data.name)
    result = await session.execute(query)
    category = result.scalars().first()

    if category:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category {category.name} already exists"
        )
    else:
        new_category = CategoryModel(**form_data.model_dump())

        session.add(new_category)

        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Category {new_category.name} already exists"
            )

        await session.refresh(new_category)

        return new_category
