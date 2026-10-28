from decimal import Decimal
from http.client import HTTPException
from typing import Literal

from fastapi import APIRouter, Query
from sqlalchemy import select, func
from starlette import status
from starlette.responses import Response

from shopapi.db.session import get_session, SessionDep
from shopapi.models.product import ProductModel
from shopapi.schemas.product import ProductResponseSchema, ProductListResponseSchema

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)

@router.get("/{product_id}", response_model=ProductResponseSchema)
async def get_product(
        product_id: int,
        session: SessionDep
):
    product = await session.get(ProductModel, product_id)

    if not product:
        return Response(
            status_code=status.HTTP_404_NOT_FOUND,
            content=f"Product with id {product_id} not found"
        )

    return product


@router.get("/", response_model=ProductListResponseSchema)
async def get_products(
        session: SessionDep,
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
            return Response(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                content="The minimum price must be less than the maximum price",
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
        query = query.where(
            ProductModel.name.ilike(f"%{search.strip()}%")
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












# @router.post("/")
# async def create_product(session: SessionDep, product: ProductAddSchema) -> ProductAddSchema:
#     new_product = ProductModel(
#         category_id = product.category_id,
#         name=product.name,
#         description=product.description,
#         price=product.price,
#         stock=product.stock,
#     )
#     # new_product = ProductModel(
#     #     id=product.id,
#     #     category_id = product.category_id,
#     #     name=product.name,
#     #     description=product.description,
#     #     price=product.price,
#     #     stock=product.stock,
#     #     is_active=product.is_active,
#     #     created_at=product.created_at,
#     # )
#     session.add(new_product)
#
#     try:
#         await session.commit()
#     except IntegrityError:
#         await session.rollback()
#         raise HTTPException(
#             status_code=409,
#             detail=f"Product {product.name} already exists",
#         )
#
#     return {
#         "category_id": new_product.category_id,
#         "name": new_product.name,
#         "description": new_product.description,
#         "price": new_product.price,
#         "stock": new_product.stock,
#     }



# ____________________________________________________________________________________________________________
    # return {
    #     "id": new_product.id,
    #     "category_id": new_product.category_id,
    #     "name": new_product.name,
    #     "description": new_product.description,
    #     "price": new_product.price,
    #     "stock": new_product.stock,
    #     "created_at": new_product.created_at,
    # }
