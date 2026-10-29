import pytest

from shopapi.models import CategoryModel

base_path = "/api/v1/products"

base_path_2 = "api/v1/categories"

@pytest.mark.asyncio
async def test_get_product_success(client, product):
    response = await client.get(f"{base_path}/{product.id}")

    # print(response.status)
    print(response.json())