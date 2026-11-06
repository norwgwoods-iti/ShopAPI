from fastapi import APIRouter, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from starlette import status

from shopapi.core.dependencies import CurrentUserDep
from shopapi.core.dependencies import SessionDep
from shopapi.models.product import ProductModel
from shopapi.models.cart import CartModel
from shopapi.schemas.cart import CartItemCreateSchema, CartItemResponseSchema, CartListResponseSchema, \
    CartItemUpdateSchema
from shopapi.services.cart import get_cart_list_response, get_cart_item_response

router = APIRouter(
    prefix="/cart",
    tags=["Cart"],
)

@router.post(
    path="/items",
    response_model=CartListResponseSchema,
)
async def add_to_cart(
        session: SessionDep,
        current_user: CurrentUserDep,
        form_data: CartItemCreateSchema,
        response: Response,
):
    product = await session.scalar(
        select(ProductModel).where(
            ProductModel.id == form_data.product_id,
        )
    )
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id='{form_data.product_id}' not found",
        )
    if not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This product is not active",
        )

    existing = await session.scalar(
        select(CartModel).where(
            CartModel.user_id == current_user.id,
            CartModel.product_id == form_data.product_id,
        )
    )
    if existing:
        new_quantity = form_data.quantity + existing.quantity
    else:
        new_quantity = form_data.quantity

    if new_quantity > product.stock:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This item is not available in this quantity",
        )

    if existing:
        existing.quantity = new_quantity
        cart_item = existing ###
        response.status_code = status.HTTP_200_OK
    else:
        cart_item = CartModel(
            user_id=current_user.id,
            product_id=form_data.product_id,
            quantity=new_quantity,
        )
        session.add(cart_item)
        response.status_code = status.HTTP_201_CREATED

    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not update cart",
        )from e

    rows = (
        await session.execute(
            select(CartModel, ProductModel)
            .join(ProductModel, ProductModel.id == CartModel.product_id)
            .where(CartModel.user_id == current_user.id)
            .order_by(CartModel.id)
        )
    ).all()

    return get_cart_list_response(rows=rows)

@router.get(
    path="/",
    response_model=CartListResponseSchema,
)
async def get_cart(
        session: SessionDep,
        current_user: CurrentUserDep,
):
    rows = (
        await session.execute(
            select(CartModel, ProductModel)
            .join(ProductModel, ProductModel.id == CartModel.product_id)
            .where(CartModel.user_id == current_user.id)
            .order_by(CartModel.id)
        )
    ).all()
    return get_cart_list_response(rows=rows)


@router.patch(
    path="/items/{item_id}",
    response_model=CartItemResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def update_cart_item(
        session: SessionDep,
        current_user: CurrentUserDep,
        item_id: int,
        form_data: CartItemUpdateSchema,
):
    result = await session.execute(
        select(CartModel, ProductModel)
        .join(ProductModel, ProductModel.id == CartModel.product_id)
        .where(
            CartModel.user_id == current_user.id,
            CartModel.id == item_id,
        )
    )
    row = result.one_or_none()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id='{item_id}' not found",
        )
    cart, product = row
    if not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This product is not active",
        )
    if form_data.quantity > product.stock:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This item is not available in this quantity",
        )
    cart.quantity = form_data.quantity
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not update quantity cart",
        )from e

    return get_cart_item_response(
        cart=cart,
        product=product,
    )


@router.delete(
    path="/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_cart_item(
        session: SessionDep,
        current_user: CurrentUserDep,
        item_id: int,
):
    result = await session.execute(
        select(CartModel)
        .where(
            CartModel.id == item_id,
            CartModel.user_id == current_user.id,
        )
    )
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id='{item_id}' not found",
        )

    await session.delete(row)
    await session.commit()
