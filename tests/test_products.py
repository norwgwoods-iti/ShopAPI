import pytest

base_path = "/api/v1/products"

@pytest.mark.asyncio
async def test_get_product_success(client, product):

    response = await client.get(
        url=f"{base_path}/{product.id}",
    )

    result = response.json()

    assert response.status_code == 200
    assert result["id"] == product.id
    assert result["category_id"] == product.category_id
    assert result["name"] == "Test product"
    assert result["description"] == "Product for testing"
    assert result["price"] == "100.00"
    assert result["stock"] == 10
    assert result["is_active"] is True
    assert "created_at" in result


@pytest.mark.negative
async def test_get_product_incorrect_id(client, product):

    product_id = 2

    response = await client.get(
        url=f"{base_path}/{product_id}",
    )

    assert response.status_code == 404
    assert response.text == f"Product with id {product_id} not found"