from typing import Literal, Annotated

from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy import select, func, delete
from sqlalchemy.exc import IntegrityError
from starlette import status

from shopapi.api.v1.endpoints.auth import get_current_user, get_current_admin
from shopapi.db.session import SessionDep
from shopapi.models import UserModel
from shopapi.models.category import CategoryModel
from shopapi.schemas.category import CategoryResponseSchema, ProductListResponseSchema, CategoryCreateSchema, \
    CategoryUpdateSchema

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.get(
    path="/",
    response_model=ProductListResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_categories(
        session: SessionDep,
        current_user: Annotated[UserModel, Depends(get_current_user)],
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
        normalized = search.strip()
        if normalized:
            query = query.where(
                CategoryModel.name.ilike(f"%{normalized}%")
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


@router.get(
    path="/{category_id}",
    response_model=CategoryResponseSchema
)
async def get_category(
        session: SessionDep,
        current_user: Annotated[UserModel, Depends(get_current_user)],
        category_id: int
):

    category = await session.get(CategoryModel, category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id='{category_id}' not found"
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
        current_admin: Annotated[UserModel, Depends(get_current_admin)]
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


@router.patch(
    path="/{category_id}",
    response_model=CategoryResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def update_category(
        session: SessionDep,
        category_id: int,
        form_data: CategoryUpdateSchema,
        current_admin: Annotated[UserModel, Depends(get_current_admin)]
):
    category = await session.get(CategoryModel, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id='{category_id}' not found"
        )

    update_data = form_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    for field, value in update_data.items():
        setattr(category, field, value)

    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category with name='{form_data.name}' already exists"
        ) from e

    await session.refresh(category)
    return category


@router.delete(
    path="/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def update_category(
        session: SessionDep,
        category_id: int,
        current_admin: Annotated[UserModel, Depends(get_current_admin)]
):
    category = await session.get(CategoryModel, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id='{category_id}' not found"
        )

    await session.delete(category)
    await session.commit()