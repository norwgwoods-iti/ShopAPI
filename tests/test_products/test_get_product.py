import pytest

from datetime import datetime
from decimal import Decimal

from tests.schemas import StrictProductResponse
from tests.utils import parse_product

base_path = "/api/v1/products"

@pytest.mark.product_id
@pytest.mark.asyncio
async def test_get_product_response_type(auth_client, product):

    response = await auth_client.get(
        url=f"{base_path}/{product.id}",
    )

    parsed = parse_product(response=response, schema=StrictProductResponse)

    assert isinstance(parsed.id, int)
    assert isinstance(parsed.category_id, int)
    assert isinstance(parsed.name, str)
    assert isinstance(parsed.description, str)
    assert isinstance(parsed.price, Decimal)
    assert isinstance(parsed.stock, int)
    assert isinstance(parsed.is_active, bool)
    assert isinstance(parsed.created_at, datetime)

    assert parsed.created_at.tzinfo is not None
    assert parsed.price.as_tuple().exponent == -2


@pytest.mark.product_id
@pytest.mark.asyncio
async def test_get_product_success_id(auth_client, product):

    response = await auth_client.get(
         url=f"{base_path}/{product.id}",
    )

    parsed = parse_product(response=response, schema=StrictProductResponse)

    assert parsed.id == product.id
    assert parsed.category_id == product.category_id
    assert parsed.name == product.name
    assert parsed.description == product.description
    assert parsed.stock == product.stock
    assert parsed.is_active == product.is_active

    assert parsed.price == product.price
    assert Decimal(parsed.price) == Decimal("100.00") #

    assert parsed.created_at == product.created_at
    assert parsed.created_at.tzinfo is not None


@pytest.mark.product_id
@pytest.mark.negative
async def test_get_product_incorrect_id(auth_client, product):

    product_id = 9999999

    response = await auth_client.get(
        url=f"{base_path}/{product_id}",
    )

    assert response.status_code == 404
    assert response.headers["Content-Type"].startswith("application/json")

    payload = response.json()

    assert payload["error"] == True
    assert payload["status_code"] == response.status_code
    assert "detail" in payload

    detail = payload["detail"]

    assert detail["message"] == f"Product with id {product_id} not found"
    assert detail["product_id"] == product_id


@pytest.mark.product_id
@pytest.mark.negative
async def test_get_product_invalid_id(auth_client, product):

    product_id = 'invalid-id'

    response = await auth_client.get(
        url=f"{base_path}/{product_id}",
    )

    assert response.status_code == 422
    assert response.headers["Content-Type"].startswith("application/json")
    assert "detail" in response.json()