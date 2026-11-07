from decimal import Decimal
from typing import Any

from httpx import AsyncClient

from shopapi.schemas.product import ProductResponseSchema


def parse_product(
        *,
        response,
        schema ,
        status_code
):
    assert response.status_code == status_code
    assert response.headers["Content-Type"].startswith("application/json")

    payload = response.json()

    parsed = schema.model_validate(payload)

    return parsed

def parse_error_detail(
        response,
        expected_status_code
):
    assert response.status_code == expected_status_code
    assert response.headers["Content-Type"].startswith("application/json")

    payload = response.json()
    assert payload["error"] is True
    assert payload["status_code"] == response.status_code
    assert "detail" in payload

    detail = payload["detail"]

    return detail

async def patch_and_parse(
        admin_client: AsyncClient,
        product_id: int,
        payload: dict[str, Any],
        *,
        base_path: str = "/api/v1/products",
        status_code: int = 200,
        schema=ProductResponseSchema,
):
    json_payload = {
        k: str(v) if isinstance(v, Decimal) else v
        for k, v in payload.items()
    }
    response = await admin_client.patch(
        url=f"{base_path}/{product_id}",
        json=json_payload
    )
    return parse_product(
        response=response,
        schema=schema,
        status_code=status_code
    )