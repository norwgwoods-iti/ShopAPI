import pytest
from httpx import AsyncClient
from sqlalchemy import select
from shopapi.models import ProductModel
@pytest.mark.asyncio
async def test_isolation_sanity_1(
        admin_client: AsyncClient,
        post_product_payload,
        db_session
):
    response = await admin_client.post(
        url="/api/v1/products/",
        json=post_product_payload
    )
    assert response.status_code == 201
    product_id = response.json()["id"]

    found = (await db_session.execute(
        select(ProductModel).where(ProductModel.id == product_id)
    )).scalar_one_or_none()
    assert found is not None, "API пишет в другую сессию - rollback не сработает"


@pytest.mark.asyncio
async def test_isolation_sanity_2(db_session):

    products = (await db_session.execute(
        select(ProductModel)
    )).scalars().all()

    assert not products, (
        f"После предыдущего теста остались товары: "
        f"{[product.id for product in products]}"
    )