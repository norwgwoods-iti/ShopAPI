from decimal import Decimal
from typing import Any

import pytest
from httpx import AsyncClient

from shopapi.schemas.cart import CartListResponseSchema
from tests.utils import parse_response_schema, parse_system_error_detail, parse_error_detail

base_path = "/api/v1/cart"


async def _parsed_add_product_to_cart(
        client: AsyncClient,
        payload: dict[str, Any]
):
    response = await client.post(
        url=f"{base_path}/items",
        json=payload,
    )
    parsed = parse_response_schema(
        response=response,
        schema=CartListResponseSchema,
        status_code=201,
    )
    return parsed


@pytest.mark.post_cart
async def test_post_cart_response_types_contract(
        auth_client: AsyncClient,
        product,
        post_cart_payload: dict[str, Any]
):
    parsed = await _parsed_add_product_to_cart(
        client=auth_client,
        payload=post_cart_payload
    )
    assert isinstance(parsed.total_amount, Decimal)
    for item in parsed.items:
        assert isinstance(item.id, int)
        assert isinstance(item.product_id, int)
        assert isinstance(item.name, str)
        assert isinstance(item.unit_price, Decimal)
        assert isinstance(item.quantity, int)
        assert isinstance(item.subtotal, Decimal)


@pytest.mark.post_cart
async def test_post_cart_field_keeps_two_decimals(
        auth_client: AsyncClient,
        product,
        post_cart_payload: dict[str, Any]
):
    parsed = await _parsed_add_product_to_cart(
        client=auth_client,
        payload=post_cart_payload
    )
    assert parsed.total_amount.as_tuple().exponent == -2
    for item in parsed.items:
        assert item.unit_price.as_tuple().exponent == -2
        assert item.subtotal.as_tuple().exponent == -2


@pytest.mark.post_cart
async def test_post_cart_success_payload(
        auth_client: AsyncClient,
        product,
        post_cart_payload: dict[str, Any]
):
    parsed = await _parsed_add_product_to_cart(
        client=auth_client,
        payload=post_cart_payload
    )
    for item in parsed.items:
        assert item.product_id == product.id
        assert item.quantity == post_cart_payload["quantity"]


@pytest.mark.post_cart
async def test_post_cart_success_get_response(
        auth_client: AsyncClient,
        product,
        post_cart_payload: dict[str, Any]
):
    parsed_post = await _parsed_add_product_to_cart(
        client=auth_client,
        payload=post_cart_payload
    )
    response_get = await auth_client.get(
        url=f"{base_path}/",
    )
    parsed_get = parse_response_schema(
        response=response_get,
        schema=CartListResponseSchema,
        status_code=200,
    )
    assert parsed_post.total_amount == parsed_get.total_amount

    (item_post,) = parsed_post.items
    (item_get,) = parsed_get.items

    assert item_post.id == item_get.id
    assert item_post.product_id == item_get.product_id
    assert item_post.name == item_get.name
    assert item_post.unit_price == item_get.unit_price
    assert item_post.quantity == item_get.quantity
    assert item_post.subtotal == item_get.subtotal


@pytest.mark.post_cart
@pytest.mark.negative
async def test_post_cart_add_product_again(
        auth_client: AsyncClient,
        product,
        post_cart_payload: dict[str, Any]
):
    payload = {
        **post_cart_payload,
        "quantity": 3,
    }
    response_first = await auth_client.post(
        url=f"{base_path}/items",
        json=payload
    )
    parsed_first = parse_response_schema(
        response=response_first,
        schema=CartListResponseSchema,
        status_code=201,
    )
    (item_first,) = parsed_first.items
    assert item_first.quantity == payload["quantity"]

    response_second = await auth_client.post(
        url=f"{base_path}/items",
        json=payload
    )
    parsed_second = parse_response_schema(
        response=response_second,
        schema=CartListResponseSchema,
        status_code=200,
    )
    (item_second,) = parsed_second.items

    assert item_second.quantity == int(item_first.quantity) + payload["quantity"]


@pytest.mark.post_cart
@pytest.mark.negative
async def test_post_cart_incorrect_id(
        admin_client: AsyncClient,
        product,
        post_cart_payload: dict[str, Any]
):
    product_id = 999999
    payload={
        **post_cart_payload,
        "product_id": product_id,
    }
    response = await admin_client.post(
        url=f"{base_path}/items",
        json=payload
    )
    parse_error_detail(
        response=response,
        expected_status_code=404,
        message_error=f"Product with id='{product_id}' not found",
    )


@pytest.mark.post_cart
@pytest.mark.negative
async def test_post_cart_quantity_exceeds_stock_product(
        auth_client: AsyncClient,
        post_cart_payload: dict[str, Any],
        product
):
    payload = {
        **post_cart_payload,
        "quantity": 999999,
    }
    response = await auth_client.post(
        url=f"{base_path}/items",
        json=payload
    )
    parse_error_detail(
        response=response,
        expected_status_code=409,
        message_error="This item is not available in this quantity"
    )


@pytest.mark.post_cart
@pytest.mark.negative
async def test_post_cart_product_hide(
        auth_client: AsyncClient,
        product,
        post_cart_payload: dict[str, Any],
        db_session,
):
    setattr(product, "is_active", False)
    await db_session.commit()

    payload = {
        **post_cart_payload,
        "product_id": product.id
    }
    response = await auth_client.post(
        url=f"{base_path}/items",
        json=payload
    )
    parse_error_detail(
        response=response,
        expected_status_code=409,
        message_error="This product is not active"
    )


""" Check Field product_id/quantity """
#types
@pytest.mark.post_cart
@pytest.mark.negative
@pytest.mark.parametrize(
    "field_name, field_value", [
        pytest.param("product_id",1.5, id="product_id-float-value"),
        pytest.param("product_id","test!@#", id="product_id-str-alphabet-and-symbols-value"),
        pytest.param("product_id","   ", id="product_id-whitespace-value"),
        pytest.param("product_id","", id="product_id-whitespace-value"),
        pytest.param("product_id",True, id="product_id-boolean-value"),
        pytest.param("product_id",None, id="product_id-None-value"),
        pytest.param("product_id",[], id="product_id-list-value"),
        pytest.param("product_id",{}, id="product_id-dict-value"),

        pytest.param("quantity",1.5, id="quantity-float-value"),
        pytest.param("quantity","test!@#", id="quantity-str-alphabet-and-symbols-value"),
        pytest.param("quantity","   ", id="quantity-whitespace-value"),
        pytest.param("quantity","", id="quantity-whitespace-value"),
        pytest.param("quantity",True, id="quantity-boolean-value"),
        pytest.param("quantity",None, id="quantity-None-value"),
        pytest.param("quantity",[], id="quantity-list-value"),
        pytest.param("quantity",{}, id="quantity-dict-value")
    ]
)
async def test_post_cart_field_invalid_types(
        auth_client: AsyncClient,
        product,
        post_cart_payload,
        field_name: str,
        field_value: Any
):
    payload = {
        **post_cart_payload,
        field_name: field_value,
    }
    response = await auth_client.post(
        url=f"{base_path}/items",
        json=payload,
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="Input should be a valid integer"
    )


@pytest.mark.post_cart
@pytest.mark.negative
@pytest.mark.parametrize(
    "field_name, field_value", [
        pytest.param("product_id", 0, id="product_id-zero"),
        pytest.param("product_id", -1, id="product_id-negative"),

        pytest.param("quantity", 0, id="quantity-zero"),
        pytest.param("quantity", -1, id="quantity-negative"),
    ]
)
async def test_post_cart_field_under_min_value(
        auth_client: AsyncClient,
        product,
        field_name: str,
        field_value: int,
        post_cart_payload: dict[str, Any]
):
    payload = {
        **post_cart_payload,
        field_name: field_value,
    }
    response = await auth_client.post(
        url=f"{base_path}/items",
        json=payload,
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="Input should be greater than 0"
    )


""" Authorization Check """
@pytest.mark.get_products
@pytest.mark.negative
async def test_post_cart_unauthorized(
        client: AsyncClient,
        products,
        post_cart_payload: dict[str, Any]
):
    response = await client.post(
        url=f"{base_path}/items",
        json=post_cart_payload,
    )
    parse_error_detail(
        response=response,
        expected_status_code=401,
        message_error="Not authenticated"
    )


@pytest.mark.get_products
@pytest.mark.negative
async def test_post_cart_invalid_token(
        auth_client: AsyncClient,
        products,
        post_cart_payload: dict[str, Any]
):
    response = await auth_client.post(
        url=f"{base_path}/items",
        headers={
            "Authorization": "invalid-token",
        },
        json=post_cart_payload,
    )
    parse_error_detail(
        response=response,
        expected_status_code=401,
        message_error="Not authenticated"
    )


@pytest.mark.get_products
async def test_post_cart_admin_token(
        admin_client: AsyncClient,
        product,
        post_cart_payload
):
    response = await admin_client.post(
        url=f"{base_path}/items",
        json=post_cart_payload,
    )
    parse_response_schema(
        response=response,
        schema=CartListResponseSchema,
        status_code=201
    )

