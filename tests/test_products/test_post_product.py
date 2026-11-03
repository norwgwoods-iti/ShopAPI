import pytest

from shopapi.models import CategoryModel
from tests.conftest import db_session

base_path = "/api/v1/products"

@pytest.mark.asyncio
@pytest.mark.post_product
async def test_post_product(admin_client, db_session):

    new_category = CategoryModel(
        name="Верхняя одежда",
        slug="verhnya-odezjda"
    )
    db_session.add(new_category)
    await db_session.commit()

    response = await admin_client.post(
        url=f"{base_path}/",
        json={
            "name": "Футболка",
            "description": "Шляпа",
            "category_id": 1,
            "price": 1000.00,
            "stock": 100,
        }
    )

    assert response.status_code == 201

    response_json = response.json()

    print(response_json)
