import pytest

from datetime import datetime
from decimal import Decimal

from httpx import AsyncClient

from tests.schemas import StrictProductResponse
from tests.utils import parse_product, parse_error_detail, parse_system_error_detail

base_path = "/api/v1/products"

@pytest.mark.get_product_id
async def test_get_product_response_type(
        auth_client: AsyncClient,
        product
):
    response = await auth_client.get(
        url=f"{base_path}/{product.id}",
    )
    parsed = parse_product(
        response=response,
        schema=StrictProductResponse,
        status_code=200
    )
    assert isinstance(parsed.id, int)
    assert isinstance(parsed.category_id, int)
    assert isinstance(parsed.name, str)
    assert isinstance(parsed.description, str)
    assert isinstance(parsed.price, Decimal)
    assert isinstance(parsed.stock, int)
    assert isinstance(parsed.is_active, bool)
    assert isinstance(parsed.created_at, datetime)


@pytest.mark.get_product_id
async def test_get_product_price_keeps_two_decimals(
        auth_client: AsyncClient,
        product
):
    response = await auth_client.get(
        url=f"{base_path}/{product.id}",
    )
    parsed = parse_product(
        response=response,
        schema=StrictProductResponse,
        status_code=200
    )
    assert parsed.price.as_tuple().exponent == -2


@pytest.mark.get_product_id
async def test_get_product_datetime_is_aware(
        auth_client: AsyncClient,
        product
):
    response = await auth_client.get(
        url=f"{base_path}/{product.id}",
    )
    parsed = parse_product(
        response=response,
        schema=StrictProductResponse,
        status_code=200
    )
    assert parsed.created_at.tzinfo is not None


@pytest.mark.get_product_id
async def test_get_product_success_id(
        auth_client: AsyncClient,
        product
):
    response = await auth_client.get(
         url=f"{base_path}/{product.id}",
    )
    parsed = parse_product(
        response=response,
        schema=StrictProductResponse,
        status_code=200
    )
    assert parsed.id == product.id
    assert parsed.category_id == product.category_id
    assert parsed.name == product.name
    assert parsed.description == product.description
    assert parsed.stock == product.stock
    assert parsed.is_active == product.is_active
    assert Decimal(parsed.price) == Decimal(product.price)
    assert parsed.created_at == product.created_at


@pytest.mark.get_product_id
@pytest.mark.negative
async def test_get_product_incorrect_id(
        auth_client: AsyncClient,
        product
):
    product_id = 9999999

    response = await auth_client.get(
        url=f"{base_path}/{product_id}",
    )
    parse_error_detail(
        response=response,
        expected_status_code=404,
        message_error=f"Product with id='{product_id}' not found"
    )


@pytest.mark.delete_product
@pytest.mark.negative
@pytest.mark.parametrize(
    "product_id", [
        pytest.param(1.5, id="product_id-float-value"),
        pytest.param("test!@#", id="product_id-str-alphabet-and-symbols-value"),
        pytest.param("   ", id="product_id-whitespace-value"),
        pytest.param(True, id="product_id-boolean-value"),
        pytest.param(None, id="product_id-None-value"),
        pytest.param([], id="product_id-list-value"),
        pytest.param({}, id="product_id-dict-value")
    ]
)
async def test_get_product_invalid_types_id(
        admin_client: AsyncClient,
        product,
        product_id
):
    response = await admin_client.delete(
        url=f"{base_path}/{product_id}"
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="Input should be a valid integer, unable to parse string as an integer"
    )


""" Authorization Check """
@pytest.mark.negative
async def test_get_product_unauthorized(
        client: AsyncClient,
        product
):
    response = await client.get(
        url=f"{base_path}/{product.id}",
    )
    parse_error_detail(
        response=response,
        expected_status_code=401,
        message_error="Not authenticated"
    )


@pytest.mark.get_product_id
@pytest.mark.negative
async def test_get_product_invalid_token(
        auth_client: AsyncClient,
        product
):
    response = await auth_client.get(
        url=f"{base_path}/{product.id}",
        headers={
            "Authorization": "invalid-token"
        }
    )
    parse_error_detail(
        response=response,
        expected_status_code=401,
        message_error="Not authenticated"
    )


@pytest.mark.get_products
async def test_get_product_admin_token(
        admin_client: AsyncClient,
        product
):
    response = await admin_client.get(
        url=f"{base_path}/{product.id}",
    )
    parse_product(
        response=response,
        schema=StrictProductResponse,
        status_code=200
    )