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
        product,
        db_session,
):
    setattr(product, "is_active", False)
    await db_session.commit()

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


@pytest.mark.update_product_status
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
async def test_update_status_invalid_types_product_id(
        admin_client: AsyncClient,
        product,
        product_id
):
    response = await admin_client.patch(
        url=f"{base_path}/{product_id}/status",
        json={
            "is_active": False
        }
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="Input should be a valid integer, unable to parse string as an integer"
    )



""" Authorization Check """
@pytest.mark.update_product_status
@pytest.mark.negative
async def test_update_status_unauthorize(
        client: AsyncClient,
        product,
        db_session
):
    setattr(product, "is_active", False)
    await db_session.commit()

    response = await client.patch(
        url=f'{base_path}/{product.id}/status',
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
        product,
        db_session
):
    setattr(product, "is_active", False)
    await db_session.commit()

    response = await client.patch(
        url=f'{base_path}/{product.id}/status',
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
        product,
        db_session
):
    setattr(product, "is_active", False)
    await db_session.commit()

    response = await auth_client.patch(
        url=f'{base_path}/{product.id}/status',
        json={
            "is_active": True,
        },
    )
    parse_error_detail(
        response=response,
        expected_status_code=403,
        message_error="Admin access required"
    )