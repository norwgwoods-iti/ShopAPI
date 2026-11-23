from datetime import datetime
from decimal import Decimal

import pytest
from httpx import AsyncClient

from shopapi.schemas.product import ProductResponseSchema
from tests.utils import parse_product, parse_error_detail, parse_system_error_detail, patch_and_parse

base_path = "/api/v1/products"

@pytest.mark.update_product
async def test_update_product_response_contract(
        admin_client: AsyncClient,
        products
):
    product = products[0]
    payload = {
        "name": "Test Update Product",
        "description": "Test Update Product",
        "category_id": 2,
        "price": "900.10",
        "stock": 27,
    }
    parsed = await patch_and_parse(
        admin_client=admin_client,
        product_id=product.id,
        payload=payload,
    )
    assert isinstance(parsed.id, int)
    assert isinstance(parsed.category_id, int)
    assert isinstance(parsed.name, str)
    assert isinstance(parsed.description, str)
    assert isinstance(parsed.price, Decimal)
    assert isinstance(parsed.stock, int)
    assert isinstance(parsed.is_active, bool)
    assert isinstance(parsed.created_at, datetime)


@pytest.mark.update_product
async def test_update_product_price_keeps_two_decimals(
        admin_client: AsyncClient,
        product
):
    parsed = await patch_and_parse(
        admin_client=admin_client,
        product_id=product.id,
        payload={
            "name": "Test Update Product",
        },
    )
    assert parsed.price.as_tuple().exponent == -2


@pytest.mark.update_product
async def test_update_product_datetime_is_aware(
        admin_client: AsyncClient,
        product
):
    parsed = await patch_and_parse(
        admin_client=admin_client,
        product_id=product.id,
        payload={
            "name": "Test Update Product",
        },
    )
    assert parsed.created_at.tzinfo is not None


@pytest.mark.update_product
async def test_update_product_success_get_response(
        admin_client: AsyncClient,
        products
):
    product = products[0]
    payload = {
        "name": "Test Update Product",
        "description": "Test Update Product",
        "category_id": 2,
        "price": "900.10",
        "stock": 27,
    }
    parsed_post = await patch_and_parse(
        admin_client=admin_client,
        product_id=product.id,
        payload=payload,
    )
    response_get = await admin_client.get(
        url=f"{base_path}/{product.id}",
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
    assert parsed_post.price == parsed_get.price
    assert parsed_post.created_at == parsed_get.created_at


@pytest.mark.update_product
async def test_update_product_success_payload(
        admin_client: AsyncClient,
        products
):
    product = products[0]
    payload = {
        "name": "Test Update Product",
        "description": "Test Update Product",
        "category_id": 2,
        "price": "900.10",
        "stock": 27,
    }
    parsed = await patch_and_parse(
        admin_client=admin_client,
        product_id=product.id,
        payload=payload,
    )
    assert parsed.id == product.id
    assert parsed.category_id == payload["category_id"]
    assert parsed.name == payload["name"]
    assert parsed.description == payload["description"]
    assert parsed.price == Decimal(str(payload["price"]))
    assert parsed.stock == payload["stock"]
    assert parsed.is_active == product.is_active
    assert parsed.created_at == product.created_at


@pytest.mark.update_product
@pytest.mark.parametrize(
    "payload_field, payload_value",
    [
        ("name", "Test Update Product"),
        ("description", "Test Update Product"),
        ("category_id", 2),
        ("price","900.10"),
        ("stock", 27),
    ]
)
async def test_update_field(
        admin_client,
        products,
        payload_field,
        payload_value,
):
    product = products[0]
    parsed = await patch_and_parse(
        admin_client=admin_client,
        product_id=product.id,
        payload={
            payload_field: payload_value
        },
    )
    if payload_field == "price":
        assert parsed.price == Decimal(str(payload_value))
    else:
        assert getattr(parsed, payload_field) == payload_value


@pytest.mark.update_product
@pytest.mark.negative
async def test_update_product_invalid_id(
        admin_client: AsyncClient,
        product
):
    product_id = "invalid-id"
    response = await admin_client.patch(
        url=f"{base_path}/{product_id}",
        json={
            "name": "Test Update Product",
        }
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="Input should be a valid integer, unable to parse string as an integer"
    )


@pytest.mark.update_product
@pytest.mark.negative
async def test_update_product_incorrect_id(
        admin_client: AsyncClient,
        product
):
    product_id = 9999999
    response = await admin_client.patch(
        url=f"{base_path}/{product_id}",
        json={
            "name": "Test Update Product",
        }
    )
    parse_error_detail(
        response=response,
        expected_status_code=404,
        message_error=f"Product with id='{product_id}' not found"
    )


@pytest.mark.update_product
@pytest.mark.negative
async def test_update_product_empty_data(
        admin_client: AsyncClient,
        product
):
    response = await admin_client.patch(
        url=f"{base_path}/{product.id}",
        json={}
    )
    parse_error_detail(
        response=response,
        expected_status_code=400,
        message_error="No fields provided for update"
    )


""" Check Field name/description (alphanumeric, special-chars) """
#validate
@pytest.mark.update_product
@pytest.mark.parametrize(
    "field_name, field_value", [
        pytest.param("name", "Test Product 2026", id="name-alphanumeric"),
        pytest.param("name", "T%$est_Pr@duct !", id="name-special-chars"),
        pytest.param("description", "Description Product 2026", id="description-alphanumeric"),
        pytest.param("description", "D@!es%cription_Pr@duct !", id="description-special-chars"),
    ]
)
async def test_patch_products_name_and_desc_non_alphabetic_chars(
        admin_client: AsyncClient,
        product,
        field_name: str,
        field_value: str
):
    payload = {
        field_name: field_value
    }
    response = await admin_client.patch(
        url=f"{base_path}/{product.id}",
        json=payload
    )
    parsed = parse_product(
        response=response,
        schema=ProductResponseSchema,
        status_code=200,
    )
    assert getattr(parsed, field_name) == field_value


""" Check Field name/description (number chars) """
@pytest.mark.update_product
@pytest.mark.negative
@pytest.mark.parametrize(
    "field_name, field_value", [
        pytest.param("name", 123, id="name-integer-value"),
        pytest.param("name", 12.3, id="name-float-value"),
        pytest.param("description", 123, id="description-integer-value"),
        pytest.param("description", 12.3, id="description-float-value"),
    ]
)
async def test_patch_products_name_and_desc_numeric_values(
        admin_client: AsyncClient,
        product,
        field_name: str,
        field_value: int | float
):
    payload = {
        field_name: field_value
    }
    response = await admin_client.patch(
        url=f"{base_path}/{product.id}",
        json=payload
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="Input should be a valid string",
    )


""" Check Field name/description (any type values) """
@pytest.mark.update_product
@pytest.mark.negative
@pytest.mark.parametrize(
    "field_name, field_value", [
        pytest.param("name", [], id="name-list-type"),
        pytest.param("name", {}, id="name-dict-type"),
        pytest.param("name", True, id="name-boolean-type"),

        pytest.param("description", [], id="description-list-type"),
        pytest.param("description", {}, id="description-dict-type"),
        pytest.param("description", True, id="description-boolean-type"),
    ]
)
async def test_patch_product_string_fields_invalid_types(
        admin_client: AsyncClient,
        product,
        field_name,
        field_value,
):
    payload = {
        field_name: field_value
    }
    response = await admin_client.patch(
        url=f"{base_path}/{product.id}",
        json=payload
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="Input should be a valid string",
    )


""" Check Field name/category_id/price/stock (None value) """
@pytest.mark.update_product
@pytest.mark.negative
@pytest.mark.parametrize(
    "field_name", [
        "name",
        "category_id",
        "price",
        "stock",
    ]
)
async def test_patch_product_none_value_fields(
        admin_client: AsyncClient,
        product,
        field_name: str
):
    payload = {
        field_name: None,
    }
    response = await admin_client.patch(
        url=f"{base_path}/{product.id}",
        json=payload
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error=f'Value error, "{field_name}" cannot be null',
    )


""" Check Field name/description (whitespace for sides) """
@pytest.mark.update_product
@pytest.mark.negative
@pytest.mark.parametrize(
    "field_name", [
        "name",
        "description",
    ]
)
async def test_patch_product_name_and_description_whitespace_sides(
        admin_client: AsyncClient,
        product,
        field_name: str
):
    payload = {
        field_name: " Whitespaces ",
    }
    response = await admin_client.patch(
        url=f"{base_path}/{product.id}",
        json=payload
    )
    parsed = parse_product(
        response=response,
        schema=ProductResponseSchema,
        status_code=200
    )
    assert getattr(parsed, field_name) == payload[field_name].strip()


""" Check Field name """
# length
@pytest.mark.update_product
@pytest.mark.parametrize(
    "name_values", [
        "n" * 199,
        "n" * 200
    ]
)
async def test_patch_product_name_max_length(
        admin_client: AsyncClient,
        product,
        name_values
):
    payload = {
        "name": name_values,
    }
    response = await admin_client.patch(
        url=f"{base_path}/{product.id}",
        json=payload
    )
    parsed = parse_product(
        response=response,
        schema=ProductResponseSchema,
        status_code=200
    )
    assert parsed.name == name_values


@pytest.mark.update_product
@pytest.mark.negative
async def test_patch_product_name_exceeds_max_length(
        admin_client: AsyncClient,
        product,
):
    payload = {
        "name": "s" * 201,
    }
    response = await admin_client.patch(
        url=f"{base_path}/{product.id}",
        json=payload
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="String should have at most 200 characters",
    )


@pytest.mark.update_product
@pytest.mark.parametrize(
    "name_values", [
        "n",
        "na"
    ]
)
async def test_patch_product_name_min_length(
        admin_client: AsyncClient,
        product,
        name_values
):
    payload = {
        "name": name_values,
    }
    response = await admin_client.patch(
        url=f"{base_path}/{product.id}",
        json=payload
    )
    parsed = parse_product(
        response=response,
        schema=ProductResponseSchema,
        status_code=200
    )
    assert parsed.name == name_values


@pytest.mark.update_product
@pytest.mark.negative
async def test_patch_product_name_under_min_length(
        admin_client: AsyncClient,
        product
):
    payload = {
        "name": "",
    }
    response = await admin_client.patch(
        url=f"{base_path}/{product.id}",
        json=payload
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="String should have at least 1 character",
    )


# whitespaces
@pytest.mark.update_product
@pytest.mark.negative
async def test_patch_product_name_whitespace_sides(
        admin_client: AsyncClient,
        product
):
    payload = {
        "name": " Whitespaces ",
    }
    response = await admin_client.patch(
        url=f"{base_path}/{product.id}",
        json=payload
    )
    parsed = parse_product(
        response=response,
        schema=ProductResponseSchema,
        status_code=200
    )
    assert parsed.name == payload["name"].strip()


@pytest.mark.update_product
@pytest.mark.negative
async def test_patch_product_name_whitespace_only(
        admin_client: AsyncClient,
        product,
):
    payload = {
        "name": "  ",
    }
    response = await admin_client.patch(
        url=f"{base_path}/{product.id}",
        json=payload
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="String should have at least 1 character",
    )


""" Check Field description """
# length
@pytest.mark.update_product
@pytest.mark.parametrize(
    "description_values", [
        "d" * 2999,
        "d" * 3000
    ]
)
async def test_patch_product_description_max_length(
        admin_client: AsyncClient,
        product,
        description_values
):
    payload = {
        "description": description_values,
    }
    response = await admin_client.patch(
        url=f"{base_path}/{product.id}",
        json=payload
    )
    parsed = parse_product(
        response=response,
        schema=ProductResponseSchema,
        status_code=200
    )
    assert parsed.description == description_values


@pytest.mark.update_product
@pytest.mark.negative
async def test_patch_product_description_exceeds_max_length(
        admin_client: AsyncClient,
        product,
):
    payload = {
        "description": "d" * 3001,
    }
    response = await admin_client.patch(
        url=f"{base_path}/{product.id}",
        json=payload
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="String should have at most 3000 characters",
    )


@pytest.mark.update_product
async def test_patch_product_description_min_length(
        admin_client: AsyncClient,
        product
):
    payload = {
        "description": "d",
    }
    response = await admin_client.patch(
        url=f"{base_path}/{product.id}",
        json=payload
    )
    parsed = parse_product(
        response=response,
        schema=ProductResponseSchema,
        status_code=200
    )
    assert parsed.description == payload["description"]


@pytest.mark.update_product
@pytest.mark.negative
@pytest.mark.parametrize(
    "description_values", [
        "",
        "   ",
        None
    ]
)
async def test_patch_product_description_none(
        admin_client: AsyncClient,
        product,
        description_values
):
    payload = {
        "description": description_values,
    }
    response = await admin_client.patch(
        url=f"{base_path}/{product.id}",
        json=payload
    )
    parsed = parse_product(
        response=response,
        schema=ProductResponseSchema,
        status_code=200
    )
    assert parsed.description is None


""" Check Field category_id """
@pytest.mark.update_product
async def test_patch_product_category_id_success(
        admin_client: AsyncClient,
        products,
        category,
        db_session
):
    payload = {
        "category_id": products[1].category_id
    }
    response = await admin_client.patch(
        url=f"{base_path}/{products[0].id}",
        json=payload
    )
    parsed = parse_product(
        response=response,
        schema=ProductResponseSchema,
        status_code=200
    )
    assert parsed.category_id == products[1].category_id


@pytest.mark.update_product
@pytest.mark.negative
@pytest.mark.parametrize(
    "field_value", [
        1.5,
        "1",
        "test!@#",
        "",
        "   ",
        True,
        [],
        {}
    ]
)
async def test_patch_product_category_id_invalid_types(
        admin_client: AsyncClient,
        product,
        field_value,
):
    payload = {
        "category_id": field_value
    }
    response = await admin_client.patch(
        url=f"{base_path}/{product.id}",
        json=payload
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="Input should be a valid integer",
    )


@pytest.mark.update_product
@pytest.mark.negative
async def test_patch_product_category_id_incorrect_value(
        admin_client: AsyncClient,
        product
):
    payload = {
        "category_id": 99999
    }
    response = await admin_client.patch(
        url=f"{base_path}/{product.id}",
        json=payload
    )
    parse_error_detail(
        response=response,
        expected_status_code=404,
        message_error=f'Category with id={payload["category_id"]} not found'
    )

@pytest.mark.update_product
@pytest.mark.negative
@pytest.mark.parametrize(
    "field_value", [
        0,
        -1
    ]
)
async def test_patch_product_category_id_under_min_value(
        admin_client: AsyncClient,
        product,
        field_value: int
):
    payload = {
        "category_id": field_value
    }
    response = await admin_client.patch(
        url=f"{base_path}/{product.id}",
        json=payload
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="Input should be greater than 0",
    )


""" Check Field price """
@pytest.mark.update_product
@pytest.mark.parametrize(
    "field_value", [
        "1200.37",
        1200.37,
        "1200",
        "1"
        "0.1"
    ]
)
async def test_patch_product_price_success(
        admin_client: AsyncClient,
        product,
        field_value
):
    payload = {
        "price": field_value
    }
    response = await admin_client.patch(
        url=f"{base_path}/{product.id}",
        json=payload
    )
    parsed = parse_product(
        response=response,
        schema=ProductResponseSchema,
        status_code=200
    )
    assert parsed.price == Decimal(str(payload["price"]))


@pytest.mark.update_product
@pytest.mark.negative
@pytest.mark.parametrize(
    "field_value", [
        0,
        -1
    ]
)
async def test_patch_product_price_under_min_value(
        admin_client: AsyncClient,
        product,
        field_value: int
):
    payload = {
        "price": field_value
    }
    response = await admin_client.patch(
        url=f"{base_path}/{product.id}",
        json=payload
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="Input should be greater than 0",
    )


@pytest.mark.update_product
@pytest.mark.negative
@pytest.mark.parametrize(
    "field_value", [
        "invalid-price",
        "!@#$",
        "  ",
        "",
    ]
)
async def test_patch_product_price_invalid_string_types(
        admin_client: AsyncClient,
        product,
        field_value
):
    payload = {
        "price": field_value
    }
    response = await admin_client.patch(
        url=f"{base_path}/{product.id}",
        json=payload
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="Input should be a valid decimal"
    )


@pytest.mark.update_product
@pytest.mark.parametrize(
    "field_value", [
        [],
        {},
        True,
    ]
)
async def test_patch_product_price_invalid_any_types(
        admin_client: AsyncClient,
        product,
        field_value
):
    payload = {
        "price": field_value
    }
    response = await admin_client.patch(
        url=f"{base_path}/{product.id}",
        json=payload
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="Decimal input should be an integer, float, string or Decimal object"
    )

""" Check Field stock """

@pytest.mark.update_product
async def test_patch_product_stock_success(
        admin_client: AsyncClient,
        product,
):
    payload = {
        "stock": 20
    }
    response = await admin_client.patch(
        url=f"{base_path}/{product.id}",
        json=payload
    )
    parsed = parse_product(
        response=response,
        schema=ProductResponseSchema,
        status_code=200
    )
    assert parsed.stock == payload["stock"]


@pytest.mark.update_product
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

    ]
)
async def test_patch_product_stock_invalid_types(
        admin_client: AsyncClient,
        product,
        field_value
):
    payload = {
        "stock": field_value
    }
    response = await admin_client.patch(
        url=f"{base_path}/{product.id}",
        json=payload
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="Input should be a valid integer"
    )


@pytest.mark.update_product
@pytest.mark.parametrize(
    "field_value", [
        0,
        1
    ]
)
async def test_patch_product_stock_min_value(
        admin_client: AsyncClient,
        product,
        field_value: int
):
    payload = {
        "stock": field_value
    }
    response = await admin_client.patch(
        url=f"{base_path}/{product.id}",
        json=payload
    )
    parsed = parse_product(
        response=response,
        schema=ProductResponseSchema,
        status_code=200
    )
    assert parsed.stock == payload["stock"]


@pytest.mark.update_product
@pytest.mark.negative
async def test_patch_product_stock_under_min_value(
        admin_client: AsyncClient,
        product,
):
    payload = {
        "stock": -1
    }
    response = await admin_client.patch(
        url=f"{base_path}/{product.id}",
        json=payload
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="Input should be greater than or equal to 0",
    )


@pytest.mark.update_product
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
async def test_update_product_invalid_types_product_id(
        admin_client: AsyncClient,
        product,
        product_id
):
    response = await admin_client.patch(
        url=f"{base_path}/{product}",
        json={
            "name": "Test Update Product",
        }
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="Input should be a valid integer, unable to parse string as an integer"
    )


""" Authorization Check """
@pytest.mark.update_product
@pytest.mark.negative
async def test_update_product_unauthorized(
        client: AsyncClient,
        product,
):
    response = await client.patch(
        url=f"{base_path}/{product.id}",
        json={
            "name": "Test Update Product",
        }
    )
    parse_error_detail(
        response=response,
        expected_status_code=401,
        message_error="Not authenticated"
    )


@pytest.mark.update_product
@pytest.mark.negative
async def test_update_product_invalid_token(
        client: AsyncClient,
        product
):
    product = product
    response = await client.patch(
        url=f"{base_path}/{product.id}",
        json={
            "name": "Test Update Product",
        },
        headers={
            "Authorization": "invalid-token"
        }
    )
    parse_error_detail(
        response=response,
        expected_status_code=401,
        message_error="Not authenticated"
    )


@pytest.mark.update_product
@pytest.mark.negative
async def test_update_product_user_token(
        auth_client: AsyncClient,
        product
):
    product = product
    response = await auth_client.patch(
        url=f"{base_path}/{product.id}",
        json={
            "name": "Test Update Product",
        }
    )
    parse_error_detail(
        response=response,
        expected_status_code=403,
        message_error="Admin access required"
    )