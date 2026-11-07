from datetime import datetime
from decimal import Decimal

import pytest

from tests.utils import parse_error_detail, patch_and_parse

base_path = "/api/v1/products"

@pytest.mark.update_product
async def test_update_product_response_type(admin_client, products):
    product = products[0]
    payload = {
        "name": "Test Update Product",
        "description": "Test Update Product",
        "category_id": 2,
        "price": Decimal("900.10"),
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
async def test_update_product_price_keeps_two_decimals(admin_client, products):
    product = products[0]
    parsed = await patch_and_parse(
        admin_client=admin_client,
        product_id=product.id,
        payload={
            "name": "Test Update Product",
        },
    )
    assert parsed.price.as_tuple().exponent == -2

@pytest.mark.update_product
async def test_update_product_datetime_is_aware(admin_client, products):
    product = products[0]
    parsed = await patch_and_parse(
        admin_client=admin_client,
        product_id=product.id,
        payload={
            "name": "Test Update Product",
        },
    )
    assert parsed.created_at.tzinfo is not None


@pytest.mark.update_product
async def test_update_product_success(admin_client, products):
    product = products[0]
    payload = {
        "name": "Test Update Product",
        "description": "Test Update Product",
        "category_id": 2,
        "price": Decimal("900.10"),
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
    assert Decimal(parsed.price) == Decimal(payload["price"])
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
        ("price",Decimal("900.10")),
        ("stock", 27),
    ]
)
async def test_update_fields(
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

    for field, value in parsed.model_dump().items():
        if payload_field == field:
            assert value == payload_value
        else:
            assert value == getattr(product, field)


@pytest.mark.update_product
@pytest.mark.negative
async def test_update_product_invalid_id(admin_client, products):
    product_id = "invalid-id"
    response = await admin_client.patch(
        url=f"{base_path}/{product_id}",
        json={
            "name": "Test Update Product",
        }
    )
    assert response.status_code == 422
    assert response.headers["Content-Type"].startswith("application/json")
    assert "detail" in response.json()


@pytest.mark.update_product
@pytest.mark.negative
async def test_update_product_incorrect_id(admin_client, products):
    product_id = 9999999
    response = await admin_client.patch(
        url=f"{base_path}/{product_id}",
        json={
            "name": "Test Update Product",
        }
    )
    assert response.status_code == 404

    detail = parse_error_detail(response=response)
    assert detail["message"] == f"Product with id='{product_id}' not found"

@pytest.mark.update_product
@pytest.mark.negative
async def test_update_product_empty_data(admin_client, products):
    product = products[0]
    response = await admin_client.patch(
        url=f"{base_path}/{product.id}",
        json={}
    )
    detail = parse_error_detail(
        response=response,
        expected_status_code=400,
    )
    assert detail["message"] == "No fields provided for update"


@pytest.mark.update_product
@pytest.mark.negative
async def test_update_product_with_user_token(auth_client, products):
    product = products[0]
    response = await auth_client.patch(
        url=f"{base_path}/{product.id}",
        json={}
    )
    detail = parse_error_detail(
        response=response,
        expected_status_code=403,
    )
    assert detail["message"] == "No fields provided for update"

# @pytest.mark.update_product
# @pytest.mark.negative
# async def test_update_product_exist_name(admin_client, products):
#     product = products[0]
#     response = await admin_client.patch(
#         url=f"{base_path}/{product.id}",
#         json={
#             "name": products[1].name,
#         }
#     )
#     detail = parse_error_detail(
#         response=response,
#         expected_status_code=409,
#     )
#     assert detail["message"] == f"Product with name='{product[0].name}' was not updated"