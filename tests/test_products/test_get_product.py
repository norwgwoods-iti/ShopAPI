import pytest

from datetime import datetime
from decimal import Decimal

from tests.schemas import StrictProductResponse
from tests.utils import parse_product, parse_error_detail

base_path = "/api/v1/products"

@pytest.mark.get_product_id
@pytest.mark.asyncio
async def test_get_product_response_type(auth_client, product):
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
async def test_get_product_price_keeps_two_decimals(auth_client, product):
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
async def test_get_product_datetime_is_aware(auth_client, product):
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
@pytest.mark.asyncio
async def test_get_product_success_id(auth_client, product):
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
async def test_get_product_incorrect_id(auth_client, product):

    product_id = 9999999

    response = await auth_client.get(
        url=f"{base_path}/{product_id}",
    )
    detail = parse_error_detail(
        response=response,
        expected_status_code=404,
    )
    assert detail["message"] == f"Product with id='{product_id}' not found"


@pytest.mark.get_product_id
@pytest.mark.negative
async def test_get_product_invalid_id(auth_client, product):
    product_id = 'invalid-id'

    response = await auth_client.get(
        url=f"{base_path}/{product_id}",
    )
    assert response.status_code == 422
    assert response.headers["Content-Type"].startswith("application/json")
    assert "detail" in response.json()

@pytest.mark.negative
async def test_get_product_no_token(client, product):
    response = await client.get(
        url=f"{base_path}/{product.id}",
    )
    detail = parse_error_detail(
        response=response,
        expected_status_code=401
    )
    assert detail == "Not authenticated"


@pytest.mark.get_product_id
@pytest.mark.negative
async def test_get_product_invalid_token(client, product):
    product_id = 1

    response = await client.get(
        url=f"{base_path}/{product_id}",
        headers={
            "Authorization": f"Bearer invalid token"
        }
    )
    detail = parse_error_detail(
        response=response,
        expected_status_code=401
    )
    assert detail["message"] == "Could not validate token"