from decimal import Decimal

from shopapi.models import CartModel, ProductModel
from shopapi.schemas.cart import CartItemResponseSchema, CartListResponseSchema

def get_cart_item_response(
        cart: CartModel,
        product: ProductModel
) -> CartItemResponseSchema:
    return CartItemResponseSchema(
        id=cart.id,
        product_id=cart.product_id,
        name=product.name,
        unit_price=product.price,
        quantity=cart.quantity,
        subtotal=product.price * cart.quantity,
    )


def get_cart_list_response(
        rows: list[tuple[CartModel, ProductModel]],
) -> CartListResponseSchema:
    items = [
        get_cart_item_response(
            cart=cart,
            product=product
        )for cart, product in rows
    ]
    total_amount = sum(
        (i.subtotal for i in items),
        start=Decimal("0.00")
    )
    return CartListResponseSchema(
        items=items,
        total_amount=total_amount
    )