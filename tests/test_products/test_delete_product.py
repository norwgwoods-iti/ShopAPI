import pytest

from httpx import AsyncClient

from tests.utils import  parse_error_detail, parse_system_error_detail

base_path = "/api/v1/products"


@pytest.mark.delete_product
async def test_delete_product_success(
        admin_client: AsyncClient,
        product
):
    response_delete = await admin_client.delete(
        url=f"{base_path}/{product.id}"
    )
    assert response_delete.status_code == 204
    assert not response_delete.content

    response_get = await admin_client.get(
        url=f"{base_path}/{product.id}"
    )
    assert response_get.status_code == 404

    parse_error_detail(
        response=response_get,
        expected_status_code=404,
        message_error=f"Product with id='{product.id}' not found"
    )


@pytest.mark.delete_product
@pytest.mark.negative
async def test_delete_product_incorrect_id(
        admin_client: AsyncClient,
        product
):
    product_id = 999999
    response = await admin_client.delete(
        url=f"{base_path}/{product_id}"
    )
    parse_error_detail(
        response=response,
        expected_status_code=404,
        message_error=f"Product with id='{product_id}' not found",
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
async def test_delete_product_invalid_types_product_id(
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
@pytest.mark.delete_product
@pytest.mark.negative
async def test_delete_product_unauthorized(
        client: AsyncClient,
        product
):
    response = await client.delete(
        url=f"{base_path}/{product.id}",
    )
    parse_error_detail(
        response=response,
        expected_status_code=401,
        message_error="Not authenticated"
    )


@pytest.mark.delete_product
@pytest.mark.negative
async def test_delete_product_invalid_token(
        admin_client: AsyncClient,
        product
):
    response = await admin_client.delete(
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


@pytest.mark.delete_product
@pytest.mark.negative
async def test_delete_product_user_token(
        auth_client: AsyncClient,
        product
):
    response = await auth_client.delete(
        url=f"{base_path}/{product.id}",
    )
    parse_error_detail(
        response=response,
        expected_status_code=403,
        message_error="Admin access required"
    )