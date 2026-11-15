import pytest
from httpx import AsyncClient

from shopapi.schemas.product import ProductStatusUpdateResponseSchema
from tests.utils import parse_product

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
    product = product_hide
    assert product.is_active is False

    payload = {
        "is_active": True,
    }
    response_patch = await admin_client.patch(
        url=f'{base_path}/{product.id}/status',
        json=payload,
    )
    parsed = parse_product(
        response=response_patch,
        schema=ProductStatusUpdateResponseSchema,
        status_code=200
    )
    assert parsed.is_active is True

    response_get = await admin_client.get(
        f'{base_path}/{product.id}',
    )
    result = response_get.json()
    assert result['is_active'] == payload['is_active']
