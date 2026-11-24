from datetime import datetime, timezone, timedelta
from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from shopapi.models import ProductModel
from shopapi.schemas.product import ProductResponseSchema
from tests.conftest import db_session
from tests.utils import parse_response_schema, parse_error_detail, parse_system_error_detail

base_path = "/api/v1/products"


async def _post_product(
        client,
        payload,
):
    response = await client.post(
        url="/api/v1/products/",
        json=payload,
    )
    return response


@pytest.mark.post_product
async def test_post_product_response_contract(
        admin_client: AsyncClient,
        post_product_payload
):
    response = await _post_product(
        admin_client,
        post_product_payload
    )
    parsed = parse_response_schema(
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
        post_product_payload
):
    response = await _post_product(
        admin_client,
        post_product_payload
    )
    parsed = parse_response_schema(
        response=response,
        schema=ProductResponseSchema,
        status_code=201
    )
    assert parsed.price.as_tuple().exponent == -2


@pytest.mark.get_product_id
async def test_post_product_datetime_is_aware(
        admin_client: AsyncClient,
        post_product_payload
):
    response = await _post_product(
        admin_client,
        post_product_payload
    )
    parsed = parse_response_schema(
        response=response,
        schema=ProductResponseSchema,
        status_code=201
    )
    assert parsed.created_at.tzinfo is not None


@pytest.mark.post_product
async def test_post_product_success_payload(
        admin_client: AsyncClient,
        post_product_payload,
        db_session
):
    response = await _post_product(
        admin_client,
        post_product_payload
    )
    parsed = parse_response_schema(
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
        post_product_payload
):
    response_post = await _post_product(
        admin_client,
        post_product_payload
    )
    response_get = await admin_client.get(
        url=f"{base_path}/{response_post.json()['id']}"
    )
    parsed_post = parse_response_schema(
        response=response_post,
        schema=ProductResponseSchema,
        status_code=201
    )
    parsed_get = parse_response_schema(
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
    assert parsed_post.price == parsed_get.price
    assert parsed_post.created_at == parsed_get.created_at


""" Check Field name/description (alphanumeric, special-chars) """
@pytest.mark.post_product
@pytest.mark.parametrize(
    "field_name, field_values", [
        pytest.param("name", "Test Product 2026", id="name-alphanumeric"),
        pytest.param("name", "T%$est_Pr@duct !", id="name-special-chars"),
        pytest.param("description", "Description Product 2026", id="description-alphanumeric"),
        pytest.param("description", "D@!es%cription_Pr@duct !", id="description-special-chars"),
    ]
)
async def test_post_products_name_and_desc_non_alphabetic_chars(
        admin_client: AsyncClient,
        post_product_payload,
        field_name: str,
        field_values: str
):
    payload = {
        **post_product_payload,
        field_name : field_values
    }
    response = await admin_client.post(
        url=f"{base_path}/",
        json=payload
    )
    parsed = parse_response_schema(
        response=response,
        schema=ProductResponseSchema,
        status_code=201,
    )
    assert getattr(parsed, field_name) == field_values


""" Check Field name/description (number chars) """
@pytest.mark.post_product
@pytest.mark.negative
@pytest.mark.parametrize(
    "field_name, field_value", [
        pytest.param("name", 123, id="name-integer-value"),
        pytest.param("name", 12.3, id="name-float-value"),
        pytest.param("description", 123, id="description-integer-value"),
        pytest.param("description", 12.3, id="description-float-value"),
    ]
)
async def test_post_products_name_and_desc_numeric_values(
        admin_client: AsyncClient,
        post_product_payload,
        field_name: str,
        field_value: int | float
):
    payload = {
        **post_product_payload,
        field_name : field_value
    }
    response = await admin_client.post(
        url=f"{base_path}/",
        json=payload
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="Input should be a valid string",
    )


""" Check Field name/description (any type values) """
@pytest.mark.post_product
@pytest.mark.negative
@pytest.mark.parametrize(
    "field_name, field_values", [
        pytest.param("name", None, id="name-None-type"),
        pytest.param("name", [], id="name-list-type"),
        pytest.param("name", {}, id="name-dict-type"),
        pytest.param("name", True, id="name-boolean-type"),

        pytest.param("description", [], id="description-list-type"),
        pytest.param("description", {}, id="description-dict-type"),
        pytest.param("description", True, id="description-boolean-type"),
    ]
)
async def test_post_product_string_fields_invalid_types(
        admin_client: AsyncClient,
        post_product_payload,
        field_name,
        field_values,

):
    payload = {
        **post_product_payload,
        field_name: field_values,
    }
    response = await admin_client.post(
        url=f"{base_path}/",
        json=payload
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="Input should be a valid string",
    )


""" Check Field name/description (whitespace for sides) """
@pytest.mark.post_product
@pytest.mark.negative
@pytest.mark.parametrize(
    "field_name", [
        "name",
        "description",
    ]
)
async def test_post_product_name_and_description_whitespace_sides(
        admin_client: AsyncClient,
        post_product_payload,
        field_name: str
):
    payload = {
        **post_product_payload,
        field_name: " Whitespaces ",
    }
    response = await admin_client.post(
        url=f"{base_path}/",
        json=payload
    )
    parsed = parse_response_schema(
        response=response,
        schema=ProductResponseSchema,
        status_code=201
    )
    assert getattr(parsed, field_name) == payload[field_name].strip()


""" Check Field name """
# length
@pytest.mark.post_product
@pytest.mark.parametrize(
    "name_values", [
        "n" * 199,
        "n" * 200
    ]
)
async def test_post_product_name_max_length(
        admin_client: AsyncClient,
        post_product_payload,
        name_values
):
    payload = {
        **post_product_payload,
        "name":name_values,
    }
    response = await admin_client.post(
        url=f"{base_path}/",
        json=payload
    )
    parsed = parse_response_schema(
        response=response,
        schema=ProductResponseSchema,
        status_code=201
    )
    assert parsed.name == name_values


@pytest.mark.post_product
@pytest.mark.negative
async def test_post_product_name_exceeds_max_length(
        admin_client: AsyncClient,
        post_product_payload,
):
    payload = {
        **post_product_payload,
        "name": "s" * 201,
    }
    response = await admin_client.post(
        url=f"{base_path}/",
        json=payload
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="String should have at most 200 characters",
    )


@pytest.mark.post_product
@pytest.mark.parametrize(
    "name_values", [
        "n",
        "na"
    ]
)
async def test_post_product_name_min_length(
        admin_client: AsyncClient,
        post_product_payload,
        name_values
):
    payload = {
        **post_product_payload,
        "name":name_values,
    }
    response = await admin_client.post(
        url=f"{base_path}/",
        json=payload
    )
    parsed = parse_response_schema(
        response=response,
        schema=ProductResponseSchema,
        status_code=201
    )
    assert parsed.name == name_values


@pytest.mark.post_product
@pytest.mark.negative
async def test_post_product_name_under_min_length(
        admin_client: AsyncClient,
        post_product_payload,
):
    payload = {
        **post_product_payload,
        "name": "",
    }
    response = await admin_client.post(
        url=f"{base_path}/",
        json=payload
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="String should have at least 1 character",
    )


# whitespaces
@pytest.mark.post_product
@pytest.mark.negative
async def test_post_product_name_space_around(
        admin_client: AsyncClient,
        post_product_payload,
):
    payload = {
        **post_product_payload,
        "name": " Whitespaces ",
    }
    response = await admin_client.post(
        url=f"{base_path}/",
        json=payload
    )
    parsed = parse_response_schema(
        response=response,
        schema=ProductResponseSchema,
        status_code=201
    )
    assert parsed.name == payload["name"].strip()


@pytest.mark.post_product
@pytest.mark.negative
async def test_post_product_name_whitespace_only(
        admin_client: AsyncClient,
        post_product_payload,
):
    payload = {
        **post_product_payload,
        "name": "  ",
    }
    response = await admin_client.post(
        url=f"{base_path}/",
        json=payload
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="String should have at least 1 character",
    )


""" Check Field description """
# length
@pytest.mark.post_product
@pytest.mark.parametrize(
    "description_values", [
        "d" * 2999,
        "d" * 3000
    ]
)
async def test_post_product_description_max_length(
        admin_client: AsyncClient,
        post_product_payload,
        description_values
):
    payload = {
        **post_product_payload,
        "description": description_values,
    }
    response = await admin_client.post(
        url=f"{base_path}/",
        json=payload
    )
    parsed = parse_response_schema(
        response=response,
        schema=ProductResponseSchema,
        status_code=201
    )
    assert parsed.description == description_values


@pytest.mark.post_product
@pytest.mark.negative
async def test_post_product_description_exceeds_max_length(
        admin_client: AsyncClient,
        post_product_payload,
):
    payload = {
        **post_product_payload,
        "description": "d" * 3001,
    }
    response = await admin_client.post(
        url=f"{base_path}/",
        json=payload
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="String should have at most 3000 characters",
    )


@pytest.mark.post_product
async def test_post_product_description_min_length(
        admin_client: AsyncClient,
        post_product_payload,
):
    payload = {
        **post_product_payload,
        "description": "d",
    }
    response = await admin_client.post(
        url=f"{base_path}/",
        json=payload
    )
    parsed = parse_response_schema(
        response=response,
        schema=ProductResponseSchema,
        status_code=201
    )
    assert parsed.description == payload["description"]


@pytest.mark.post_product
@pytest.mark.negative
@pytest.mark.parametrize(
    "description_values", [
        "",
        "   ",
        None
    ]
)
async def test_post_product_description_none(
        admin_client: AsyncClient,
        post_product_payload,
        description_values
):
    payload = {
        **post_product_payload,
        "description": description_values,
    }
    response = await admin_client.post(
        url=f"{base_path}/",
        json=payload
    )
    parsed = parse_response_schema(
        response=response,
        schema=ProductResponseSchema,
        status_code=201
    )
    assert parsed.description is None


""" Check Field category_id """
@pytest.mark.post_product
async def test_post_product_category_id_success(
        admin_client: AsyncClient,
        post_product_payload,
        category,
        db_session
):
    payload = {
        **post_product_payload,
        "category_id": category.id
    }
    response = await admin_client.post(
        url=f"{base_path}/",
        json=payload
    )
    parsed = parse_response_schema(
        response=response,
        schema=ProductResponseSchema,
        status_code=201
    )
    assert parsed.category_id == category.id


@pytest.mark.post_product
@pytest.mark.negative
@pytest.mark.parametrize(
    "field_value", [
        1.5,
        "1",
        "test!@#",
        "",
        "   ",
        True,
        None,
        [],
        {}
    ]
)
async def test_post_product_category_id_invalid_types(
        admin_client: AsyncClient,
        post_product_payload,
        field_value,
):
    payload = {
        **post_product_payload,
        "category_id": field_value
    }
    response = await admin_client.post(
        url=f"{base_path}/",
        json=payload
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="Input should be a valid integer",
    )


@pytest.mark.post_product
@pytest.mark.negative
async def test_post_product_category_id_incorrect_value(
        admin_client: AsyncClient,
        post_product_payload,
):
    payload = {
        **post_product_payload,
        "category_id": 99999
    }
    response = await admin_client.post(
        url=f"{base_path}/",
        json=payload
    )
    parse_error_detail(
        response=response,
        expected_status_code=404,
        message_error=f"Category with id={payload["category_id"]} not found"
    )


@pytest.mark.post_product
@pytest.mark.negative
@pytest.mark.parametrize(
    "field_value", [
        0,
        -1
    ]
)
async def test_post_product_category_id_under_min_value(
        admin_client: AsyncClient,
        post_product_payload,
        field_value: int
):
    payload = {
        **post_product_payload,
        "category_id": field_value
    }
    response = await admin_client.post(
        url=f"{base_path}/",
        json=payload
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="Input should be greater than 0",
    )


""" Check Field price """
@pytest.mark.post_product
@pytest.mark.parametrize(
    "field_value", [
        "1200.37",
        1200.37,
        "1200",
        "1"
        "0.1"
    ]
)
async def test_post_product_price_success(
        admin_client: AsyncClient,
        post_product_payload,
        field_value
):
    payload = {
        **post_product_payload,
        "price": field_value
    }
    response = await admin_client.post(
        url=f"{base_path}/",
        json=payload
    )
    parsed = parse_response_schema(
        response=response,
        schema=ProductResponseSchema,
        status_code=201
    )
    assert parsed.price == Decimal(str(payload["price"]))


@pytest.mark.post_product
@pytest.mark.negative
@pytest.mark.parametrize(
    "field_value", [
        0,
        -1
    ]
)
async def test_post_product_price_under_min_value(
        admin_client: AsyncClient,
        post_product_payload,
        field_value: int
):
    payload = {
        **post_product_payload,
        "price": field_value
    }
    response = await admin_client.post(
        url=f"{base_path}/",
        json=payload
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="Input should be greater than 0",
    )


@pytest.mark.post_product
@pytest.mark.negative
@pytest.mark.parametrize(
    "field_value", [
        "invalid-price",
        "!@#$",
        "  ",
        "",
    ]
)
async def test_post_product_price_invalid_string_types(
        admin_client: AsyncClient,
        post_product_payload,
        field_value
):
    payload = {
        **post_product_payload,
        "price": field_value
    }
    response = await admin_client.post(
        url=f"{base_path}/",
        json=payload
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="Input should be a valid decimal"
    )


@pytest.mark.post_product
@pytest.mark.parametrize(
    "field_value", [
        [],
        {},
        True,
        None
    ]
)
async def test_post_product_price_invalid_any_types(
        admin_client: AsyncClient,
        post_product_payload,
        field_value
):
    payload = {
        **post_product_payload,
        "price": field_value
    }
    response = await admin_client.post(
        url=f"{base_path}/",
        json=payload
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="Decimal input should be an integer, float, string or Decimal object"
    )


""" Check Field stock """
@pytest.mark.post_product
async def test_post_product_stock_success(
        admin_client: AsyncClient,
        post_product_payload,
):
    payload = {
        **post_product_payload,
        "stock": 20
    }
    response = await admin_client.post(
        url=f"{base_path}/",
        json=payload
    )
    parsed = parse_response_schema(
        response=response,
        schema=ProductResponseSchema,
        status_code=201
    )
    assert parsed.stock == payload["stock"]


@pytest.mark.post_product
@pytest.mark.negative
@pytest.mark.parametrize(
    "field_value", [
        "invalid-price",
        "!@#$",
        "  ",
        "",
        "20",
        12.6,
        [],
        {},
        True,
        None,
    ]
)
async def test_post_product_stock_invalid_types(
        admin_client: AsyncClient,
        post_product_payload,
        field_value
):
    payload = {
        **post_product_payload,
        "stock": field_value
    }
    response = await admin_client.post(
        url=f"{base_path}/",
        json=payload
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="Input should be a valid integer"
    )


@pytest.mark.post_product
@pytest.mark.parametrize(
    "field_value", [
        0,
        1
    ]
)
async def test_post_product_stock_min_value(
        admin_client: AsyncClient,
        post_product_payload,
        field_value: int
):
    payload = {
        **post_product_payload,
        "stock": field_value
    }
    response = await admin_client.post(
        url=f"{base_path}/",
        json=payload
    )
    parsed = parse_response_schema(
        response=response,
        schema=ProductResponseSchema,
        status_code=201
    )
    assert parsed.stock == payload["stock"]


@pytest.mark.post_product
@pytest.mark.negative
async def test_post_product_stock_under_min_value(
        admin_client: AsyncClient,
        post_product_payload,
):
    payload = {
        **post_product_payload,
        "stock": -1
    }
    response = await admin_client.post(
        url=f"{base_path}/",
        json=payload
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="Input should be greater than or equal to 0",
    )


""" Check Field is_active """
@pytest.mark.post_product
@pytest.mark.parametrize(
    "field_value", [
        True,
        False,
        "True",
        "False"
    ]
)
async def test_post_product_is_active_success(
        admin_client: AsyncClient,
        post_product_payload,
        field_value
):
    payload = {
        **post_product_payload,
        "is_active": field_value
    }
    response = await admin_client.post(
        url=f"{base_path}/",
        json=payload
    )
    parsed = parse_response_schema(
        response=response,
        schema=ProductResponseSchema,
        status_code=201
    )
    assert str(parsed.is_active) == str(payload["is_active"])


@pytest.mark.post_product
@pytest.mark.negative
@pytest.mark.parametrize(
    "field_value", [
        "invalid-price",
        "!@#$",
        "  ",
        "",
        "20",
        20,
    ]
)
async def test_post_product_is_active_invalid_to_interpret(
        admin_client: AsyncClient,
        post_product_payload,
        field_value
):
    payload = {
        **post_product_payload,
        "is_active": field_value
    }
    response = await admin_client.post(
        url=f"{base_path}/",
        json=payload
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="Input should be a valid boolean, unable to interpret input"
    )


@pytest.mark.post_product
@pytest.mark.negative
@pytest.mark.parametrize(
    "field_value", [
        12.6,
        [],
        {},
        None,
    ]
)
async def test_post_product_is_active_invalid_any_types(
        admin_client: AsyncClient,
        post_product_payload,
        field_value
):
    payload = {
        **post_product_payload,
        "is_active": field_value
    }
    response = await admin_client.post(
        url=f"{base_path}/",
        json=payload
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="Input should be a valid boolean"
    )


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