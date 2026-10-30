from decimal import Decimal

import pytest

base_path = "/api/v1/products"

async def get_products_success(client, products):
    response = await client.get(
        url=f"{base_path}/",
    )
    result = response.json()

    assert response.status_code == 200
    assert result["total"] == len(products)
    assert result["page"] == 1
    assert result["page_size"] == 20
    assert "items" in result
    assert len(result["items"]) == result["total"]

    product = result["items"][0]
    assert {
        'id', 'category_id', 'name', 'description',
        'price', 'stock', 'is_active', 'created_at'
    } <= set(product.keys())

    return response





@pytest.mark.asyncio
async def test_get_product_success(client, product):
    response = await client.get(
        url=f"{base_path}/",
    )

    result = response.json()

    assert response.status_code == 200
    assert result["total"] == 1
    assert result["page"] == 1
    assert result["page_size"] == 20
    assert "items" in result
    assert result["items"][0]["id"] == product.id
    assert result["items"][0]["category_id"] == product.category_id
    assert result["items"][0]["name"] == "Test product"
    assert result["items"][0]["description"] == "Product for testing"
    assert result["items"][0]["price"] == "100.00"
    assert result["items"][0]["stock"] == 10
    assert result["items"][0]["is_active"] is True
    assert "created_at" in result["items"][0]


@pytest.mark.asyncio
async def test_get_products_success(client, products):

    response = await get_products_success(client, products)


@pytest.mark.asyncio
async def test_get_products_filter_empty_page(client, product):

    response = await client.get(
        url=f"{base_path}/",
        params={
            "page": 9
        },
    )

    result = response.json()

    assert response.status_code == 200
    assert result["total"] == 1
    assert result["page"] == 9
    assert result["page_size"] == 20
    assert result["items"] == []


@pytest.mark.asyncio
async def test_get_products_filter_page_size(client, products):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "page_size": 2,
        }
    )

    result = response.json()

    assert response.status_code == 200
    assert result["total"] == len(products)
    assert result["page"] == 1
    assert result["page_size"] == 2
    assert len(result["items"]) == 2



@pytest.mark.asyncio
async def test_get_products_filter_category_id(client, products):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "category_id": 2,
        }
    )

    result = response.json()

    assert response.status_code == 200
    assert result["total"] == 2
    assert result["page"] == 1
    assert result["page_size"] == 20
    assert len(result["items"]) == result["total"]


@pytest.mark.asyncio
async def test_get_products_filter_min_price(client, products):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "min_price": 2000.00,
        }
    )

    result = response.json()

    assert response.status_code == 200
    assert result["total"] == 2
    assert result["page"] == 1
    assert result["page_size"] == 20
    assert len(result["items"]) == result["total"]


@pytest.mark.asyncio
async def test_get_products_filter_max_price(client, products):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "max_price": 1200.00,
        }
    )

    result = response.json()

    assert response.status_code == 200
    assert result["total"] == 2
    assert result["page"] == 1
    assert result["page_size"] == 20
    assert len(result["items"]) == result["total"]


@pytest.mark.asyncio
async def test_get_products_filter_min_max_price(client, products):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "min_price": 1500.00,
            "max_price": 2000.00,
        }
    )

    result = response.json()

    assert response.status_code == 200
    assert result["total"] == 1
    assert result["page"] == 1
    assert result["page_size"] == 20
    assert len(result["items"]) == result["total"]


@pytest.mark.asyncio
async def test_get_products_filter_search(client, products):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "search": "2",
        }
    )

    result = response.json()

    assert response.status_code == 200
    assert result["total"] == 1
    assert result["page"] == 1
    assert result["page_size"] == 20
    assert len(result["items"]) == result["total"]


@pytest.mark.asyncio
async def test_get_products_sort_by_price_asc(client, products):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "sort_by": "price",
            "order": "asc",
        }
    )

    result = response.json()

    assert response.status_code == 200
    assert result["total"] == len(products)
    assert result["page"] == 1
    assert result["page_size"] == 20
    assert len(result["items"]) == result["total"]

    product = result["items"][0]

    assert product["id"] == 1
    assert product["category_id"] == 1
    assert product["name"] == "Test product 1"

    min_price = min((p["price"]) for p in result["items"])

    assert product["price"] == min_price



@pytest.mark.asyncio
async def test_get_products_sort_by_price_desc(client, products):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "sort_by": "price",
            "order": "desc",
        }
    )

    result = response.json()

    assert response.status_code == 200
    assert result["total"] == len(products)
    assert result["page"] == 1
    assert result["page_size"] == 20
    assert len(result["items"]) == result["total"]

    product = result["items"][0]
    assert product["id"] == 3
    assert product["category_id"] == 2

    assert product["name"] == "Test product 3"

    max_price = max((p["price"]) for p in result["items"])

    assert product["price"] == max_price


@pytest.mark.asyncio
async def test_get_product_success_id(client, product):

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

    product_id = 9999999

    response = await client.get(
        url=f"{base_path}/{product_id}",
    )

    assert response.status_code == 404
    assert response.text == f"Product with id {product_id} not found"


@pytest.mark.negative
async def test_get_product_invalid_id(client, product):

    product_id = 'invalid-id'

    response = await client.get(
        url=f"{base_path}/{product_id}",
    )

    assert response.status_code == 422
