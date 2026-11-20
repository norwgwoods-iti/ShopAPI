import pytest
from httpx import AsyncClient

from shopapi.schemas.product import ProductStatusUpdateResponseSchema
from tests.utils import parse_product, parse_system_error_detail, parse_error_detail

base_path = 'api/v1/products'

@pytest.mark.update_product_status
@pytest.mark.asyncio
async def test_update_status_product_false(
        admin_client: AsyncClient,
        product,
):
    assert product.is_active is True
    payload = {
        "is_active": False,
    }
    response_patch = await admin_client.patch(
        f'{base_path}/{product.id}/status',
        json=payload,
    )
    parsed = parse_product(
        response=response_patch,
        schema=ProductStatusUpdateResponseSchema,
        status_code=200
    )
    assert parsed.is_active is False

    response_get = await admin_client.get(
        f'{base_path}/{product.id}',
    )
    result = response_get.json()
    assert result['is_active'] == payload['is_active']


@pytest.mark.update_product_status
@pytest.mark.asyncio
async def test_update_status_product_true(
        admin_client: AsyncClient,
        product_hide,
        db_session,
):
    assert product_hide.is_active is False

    payload = {
        "is_active": True,
    }
    response_patch = await admin_client.patch(
        url=f'{base_path}/{product_hide.id}/status',
        json=payload,
    )
    parsed = parse_product(
        response=response_patch,
        schema=ProductStatusUpdateResponseSchema,
        status_code=200
    )
    assert parsed.is_active is True

    response_get = await admin_client.get(
        f'{base_path}/{product_hide.id}',
    )
    result = response_get.json()
    assert result['is_active'] == payload['is_active']


@pytest.mark.update_product_status
@pytest.mark.negative
@pytest.mark.parametrize(
    "check_values", [
        " ", "abcd", 123, "@#$%!"
    ]
)
async def test_update_status_product_invalid_payload(
        admin_client: AsyncClient,
        product,
        check_values: str,
):
    payload = {
        "is_active": check_values,
    }
    response = await admin_client.patch(
        url=f'{base_path}/{product.id}/status',
        json=payload
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="Input should be a valid boolean, unable to interpret input",
        input_value=check_values,
    )


@pytest.mark.update_product_status
@pytest.mark.negative
async def test_update_status_product_no_body(
        admin_client: AsyncClient,
        product,
):
    response = await admin_client.patch(
        url=f'{base_path}/{product.id}/status',
        json={},
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="Field required",
    )


""" Authorization Check """
@pytest.mark.update_product_status
@pytest.mark.negative
async def test_update_status_unauthorize(
        client: AsyncClient,
        product_hide,
):
    response = await client.patch(
        url=f'{base_path}/{product_hide.id}/status',
        json={
            "is_active": True,
        },
    )
    parse_error_detail(
        response=response,
        expected_status_code=401,
        message_error="Not authenticated"
    )


@pytest.mark.update_product_status
@pytest.mark.negative
async def test_update_status_invalid_token(
        client: AsyncClient,
        product_hide,
):
    response = await client.patch(
        url=f'{base_path}/{product_hide.id}/status',
        headers={
            "Authorization": "invalid-token",
        },
        json={
            "is_active": True,
        },
    )
    parse_error_detail(
        response=response,
        expected_status_code=401,
        message_error="Not authenticated"
    )


@pytest.mark.update_product_status
@pytest.mark.negative
async def test_update_status_with_user_token(
        auth_client: AsyncClient,
        product_hide,
):
    response = await auth_client.patch(
        url=f'{base_path}/{product_hide.id}/status',
        json={
            "is_active": True,
        },
    )
    parse_error_detail(
        response=response,
        expected_status_code=403,
        message_error="Admin access required"
    )