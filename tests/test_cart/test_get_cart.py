from decimal import Decimal
from typing import Any
import pytest
from httpx import AsyncClient

from shopapi.schemas.cart import CartListResponseSchema
from tests.utils import parse_response_schema

base_path = "/api/v1/cart"


async def _parsed_get_cart(
        client: AsyncClient,
):
    response = await client.get(
        url=f"{base_path}/",
    )
    parsed = parse_response_schema(
        response=response,
        schema=CartListResponseSchema,
        status_code=200
    )
    return parsed


@pytest.mark.get_cart
@pytest.mark.negative
async def test_():
    ...


@pytest.mark.get_cart
async def test_get_cart_response_types_contract(
        auth_client: AsyncClient,
        post_cart_one_product
):
    parsed = await _parsed_get_cart(
        client=auth_client
    )
    assert isinstance(parsed.total_amount, Decimal)
    for item in parsed.items:
        assert isinstance(item.id, int)
        assert isinstance(item.product_id, int)
        assert isinstance(item.name, str)
        assert isinstance(item.unit_price, Decimal)
        assert isinstance(item.quantity, int)
        assert isinstance(item.subtotal, Decimal)


@pytest.mark.get_cart
async def test_get_cart_field_keeps_two_decimals(
        auth_client: AsyncClient,
        post_cart_one_product
):
    parsed = await _parsed_get_cart(
        client=auth_client
    )
    assert parsed.total_amount.as_tuple().exponent == -2
    for item in parsed.items:
        assert item.unit_price.as_tuple().exponent == -2
        assert item.subtotal.as_tuple().exponent == -2


@pytest.mark.get_cart
async def test_get_cart_success_get_response(
        auth_client: AsyncClient,
        product,
        post_cart_payload: dict[str, Any]
):
    response_post = await auth_client.post(
        url=f"{base_path}/items",
        json=post_cart_payload
    )
    parsed_post = parse_response_schema(
        response=response_post,
        schema=CartListResponseSchema,
        status_code=201
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


@pytest.mark.get_cart
async def test_get_cart_success_payload(
        auth_client: AsyncClient,
        post_cart_one_product,
        product,
        post_cart_payload
):
    parsed = await _parsed_get_cart(
        client=auth_client
    )
    for item in parsed.items:
        assert item.product_id == product.id
        assert item.quantity == post_cart_payload["quantity"]


@pytest.mark.get_cart
async def test_get_cart_empty(
        auth_client: AsyncClient,
):
    parsed = await _parsed_get_cart(
        client=auth_client
    )
    assert parsed.total_amount == 0
    assert parsed.items == [] or None


@pytest.mark.get_cart
async def test_get_cart_unit_price(
        auth_client: AsyncClient,
        post_cart_payload: dict[str, Any],
        product
):
    parsed = await _parsed_get_cart(
        client=auth_client
    )
    for item in parsed.items:
        assert item.unit_price == product.price


@pytest.mark.get_cart
async def test_get_cart_name(
        auth_client: AsyncClient,
        post_cart_one_product,
        product
):
    parsed = await _parsed_get_cart(
        client=auth_client
    )
    for item in parsed.items:
        assert item.name == product.name


@pytest.mark.get_cart
async def test_get_cart_subtotal(
        auth_client: AsyncClient,
        post_cart_payload: dict[str, Any],
        product
):
    parsed = await _parsed_get_cart(
        client=auth_client
    )
    execute_subtotal = int(post_cart_payload["quantity"]) * int(product.price)
    for item in parsed.items:
        assert item.subtotal == execute_subtotal


@pytest.mark.get_cart
async def test_get_cart_total_amount_one_product(
     auth_client: AsyncClient,
     product,
     post_cart_one_product,
    post_cart_payload: dict[str, Any],
):
    parsed = await _parsed_get_cart(
        client=auth_client
    )
    execute_subtotal = int(post_cart_payload["quantity"]) * int(product.price)
    assert parsed.total_amount == execute_subtotal


@pytest.mark.get_cart
async def test_get_cart_total_amount_many_products(
        auth_client: AsyncClient,
        post_cart_many_products,
        products,
        post_cart_payload: dict[str, Any],
):
    parsed = await _parsed_get_cart(
        client=auth_client
    )
    expected_parsed_total_amount = sum(
        (item.unit_price * item.quantity for item in parsed.items),
        start=Decimal("0.00")
    )
    expected_total_amount = [p.price * post_cart_payload["quantity"] for p in products]

    assert parsed.total_amount == sum(expected_total_amount) == expected_parsed_total_amount


@pytest.mark.get_cart
async def test_get_cart_assert_unit_price_and_product_price(
     auth_client: AsyncClient,
     product,
     post_cart_payload
):
    parsed = await _parsed_get_cart(
        client=auth_client
    )
    for item in parsed.items:
        assert item.unit_price == product.price
