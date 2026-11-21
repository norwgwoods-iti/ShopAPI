from datetime import datetime, timezone, timedelta
from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from shopapi.models import ProductModel
from shopapi.schemas.product import ProductResponseSchema
from tests.conftest import db_session
from tests.utils import parse_product, parse_error_detail

base_path = "/api/v1/products"


@pytest.mark.post_product
async def test_post_product_response_type(
        admin_client: AsyncClient,
        post_product
):
    response = post_product
    parsed = parse_product(
        response=response,
        schema=ProductResponseSchema,
        status_code=201
    )
    assert isinstance(parsed.id, int)
    assert isinstance(parsed.category_id, int)
    assert isinstance(parsed.name, str)
    assert isinstance(parsed.description, str)
    assert isinstance(parsed.price, Decimal)
    assert isinstance(parsed.stock, int)
    assert isinstance(parsed.is_active, bool)
    assert isinstance(parsed.created_at, datetime)


@pytest.mark.post_product
async def test_post_product_price_keeps_two_decimals(
        admin_client: AsyncClient,
        post_product
):
    response = post_product
    parsed = parse_product(
        response=response,
        schema=ProductResponseSchema,
        status_code=201
    )
    assert parsed.price.as_tuple().exponent == -2


@pytest.mark.get_product_id
async def test_post_product_datetime_is_aware(
        admin_client: AsyncClient,
        post_product
):
    response = post_product
    parsed = parse_product(
        response=response,
        schema=ProductResponseSchema,
        status_code=201
    )
    assert parsed.created_at.tzinfo is not None


@pytest.mark.post_product
async def test_post_product_success_payload(
        admin_client: AsyncClient,
        post_product,
        post_product_payload,
        db_session
):
    response = post_product
    parsed = parse_product(
        response=response,
        schema=ProductResponseSchema,
        status_code=201
    )
    saved_product = (await db_session.execute(
        select(ProductModel).where(ProductModel.id == parsed.id)
    )).scalar_one_or_none()
    assert saved_product is not None

    assert parsed.id == saved_product.id
    assert parsed.category_id == post_product_payload["category_id"]
    assert parsed.name == post_product_payload["name"]
    assert parsed.description == post_product_payload["description"]
    assert parsed.stock == post_product_payload["stock"]
    assert parsed.is_active is True
    assert Decimal(parsed.price) == Decimal(post_product_payload["price"])

    now = datetime.now(timezone.utc)
    assert now - timedelta(minutes=1) <= parsed.created_at <= now + timedelta(seconds=5)


@pytest.mark.post_product
async def test_post_product_success_get_response(
        admin_client: AsyncClient,
        post_product,
):
    response_post = post_product

    response_get = await admin_client.get(
        url=f"{base_path}/{response_post.json()['id']}"
    )
    parsed_post = parse_product(
        response=response_post,
        schema=ProductResponseSchema,
        status_code=201
    )
    parsed_get = parse_product(
        response=response_get,
        schema=ProductResponseSchema,
        status_code=200
    )
    assert parsed_post.id == parsed_get.id
    assert parsed_post.category_id == parsed_get.category_id
    assert parsed_post.name == parsed_get.name
    assert parsed_post.description == parsed_get.description
    assert parsed_post.stock == parsed_get.stock
    assert parsed_post.is_active == parsed_get.is_active
    assert Decimal(parsed_post.price) == Decimal(parsed_get.price)
    assert parsed_post.created_at == parsed_get.created_at


""" Authorization Check """
@pytest.mark.post_product
@pytest.mark.negative
async def test_post_product_unauthorized(
        client: AsyncClient,
        post_product_payload,
):
    response = await client.post(
        url=f"{base_path}/",
        json=post_product_payload,
    )
    parse_error_detail(
        response=response,
        expected_status_code=401,
        message_error="Not authenticated",
    )


@pytest.mark.post_product
@pytest.mark.negative
async def test_post_product_invalid_token(
        client: AsyncClient,
        post_product_payload,
):
    response = await client.post(
        url=f"{base_path}/",
        headers={
            "Authorization": "invalid-token",
        },
        json=post_product_payload,
    )
    parse_error_detail(
        response=response,
        expected_status_code=401,
        message_error="Not authenticated"
    )


@pytest.mark.post_product
@pytest.mark.negative
async def test_post_product_user_token(
        auth_client: AsyncClient,
        post_product_payload,
):
    response = await auth_client.post(
        url=f"{base_path}/",
        json=post_product_payload,
    )
    parse_error_detail(
        response=response,
        expected_status_code=403,
        message_error="Admin access required"
    )

# payload = {
#   **product_payload
#   "name"="Шляпа"
# }