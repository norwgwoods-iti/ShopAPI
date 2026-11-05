from typing import Literal
from decimal import Decimal

from fastapi import HTTPException, APIRouter, Query
from starlette import status
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from shopapi.core.dependencies import CurrentUserDep, CurrentAdminDep
from shopapi.core.dependencies import SessionDep
from shopapi.models.product import ProductModel
from shopapi.schemas.product import (ProductResponseSchema, ProductListResponseSchema, ProductCreateSchema,
                                     ProductUpdateSchema)

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)

@router.get(
    path="/{product_id}",
    response_model=ProductResponseSchema
)
async def get_product(
        product_id: int,
        current_user: CurrentUserDep,
        session: SessionDep
):
    product = await session.get(ProductModel, product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Product with id='{product_id}' not found",
                "product_id": product_id,
            }
        )

    return product


@router.get(
    path="/",
    response_model=ProductListResponseSchema
)
async def get_products(
        session: SessionDep,
        current_user: CurrentUserDep,
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100),
        category_id: int | None = Query(default=None, ge=1),
        min_price: Decimal | None = Query(default=None, ge=0),
        max_price: Decimal | None = Query(default=None, ge=0),
        search: str | None = Query(default=None, min_length=1, max_length=100),
        sort_by: Literal["price", "name", "created_at"] = "created_at",
        order: Literal["desc", "asc"] = "desc",
):
    if min_price is not None and max_price is not None:
        if min_price > max_price:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={
                    "message": "The minimum price must be less than the maximum price"
                }
            )

    query = (
        select(ProductModel)
        .where(ProductModel.is_active.is_(True))
    )

    if category_id is not None:
        query = query.where(
            ProductModel.category_id == category_id
    )

    if min_price is not None:
        query = query.where(
            ProductModel.price >= min_price
        )

    if max_price is not None:
        query = query.where(
            ProductModel.price <= max_price
        )

    if search is not None:
        normalized = search.strip()
        if normalized:
            query = query.where(
                ProductModel.name.ilike(f"%{normalized}%")
            )

    sort_column = {
        "price": ProductModel.price,
        "name": ProductModel.name,
        "created_at": ProductModel.created_at,
    }[sort_by]

    if order == "asc":
        query = query.order_by(sort_column.asc(), ProductModel.id.asc())
    else:
        query = query.order_by(sort_column.desc(), ProductModel.id.desc())


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


@router.post(
    path="/",
    response_model=ProductResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
        product: ProductCreateSchema,
        session: SessionDep,
        current_admin: CurrentAdminDep,
):
    new_product = ProductModel(**product.model_dump())

    session.add(new_product)

    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product violates integrity constraints",
        ) from e

    await session.refresh(new_product)
    return new_product

@router.patch(
    path="/{product_id}",
    response_model=ProductResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def update_product(
        session: SessionDep,
        product_id: int,
        form_data: ProductUpdateSchema,
        current_admin: CurrentAdminDep,
):
    product = await session.get(ProductModel, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id='{product_id}' not found",
        )

    update_data = form_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    for field, value in update_data.items():
        setattr(product, field, value)

    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Product with name='{form_data.name}' already exists"
        ) from e

    await session.refresh(product)
    return product


@router.delete(
    path="/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_product(
        session: SessionDep,
        product_id: int,
        current_admin: CurrentAdminDep,
):
    product = await session.get(ProductModel, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id='{product_id}' not found",
        )

    await session.delete(product)
    await session.commit()
