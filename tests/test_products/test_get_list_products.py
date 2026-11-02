from datetime import datetime
from decimal import Decimal

import pytest

from tests.schemas import StrictProductListResponse
from tests.utils import parse_product, http_except_error_detail

base_path = "/api/v1/products"

@pytest.mark.products
@pytest.mark.asyncio
async def test_get_products_contract(client, products):
    response = await client.get(
        url=f"{base_path}/",
    )

    parsed = parse_product(
        response=response,
        schema=StrictProductListResponse
    )

    assert isinstance(parsed.total, int)
    assert isinstance(parsed.page, int)
    assert isinstance(parsed.page_size, int)
    assert isinstance(parsed.items, list)

    for item in parsed.items:
        assert isinstance(item.id, int)
        assert isinstance(item.category_id, int)
        assert isinstance(item.name, str)
        assert isinstance(item.description, str | None)
        assert isinstance(item.price, Decimal)
        assert isinstance(item.stock, int)
        assert isinstance(item.is_active, bool)
        assert isinstance(item.created_at, datetime)

        assert item.created_at.tzinfo is not None
        assert item.price.as_tuple().exponent == -2


@pytest.mark.products
@pytest.mark.asyncio
async def test_get_product_success(client, product):
    response = await client.get(
        url=f"{base_path}/",
    )

    parsed = parse_product(
        response=response,
        schema=StrictProductListResponse
    )

    assert parsed.total == 1
    assert parsed.page == 1
    assert parsed.page_size == 20
    assert len(parsed.items) == parsed.total

    parsed_item = parsed.items[0]

    assert parsed_item.id == product.id
    assert parsed_item.category_id == product.category_id
    assert parsed_item.name == product.name
    assert parsed_item.description == product.description
    assert Decimal(parsed_item.price) == Decimal(product.price)
    assert parsed_item.stock == product.stock
    assert parsed_item.is_active == product.is_active

    assert parsed_item.created_at == product.created_at
    assert parsed_item.created_at.tzinfo is not None


@pytest.mark.products
@pytest.mark.asyncio
async def test_get_products_success(client, products):
    response = await client.get(
        url=f"{base_path}/",
    )

    parsed = parse_product(
        response=response,
        schema=StrictProductListResponse
    )

    assert parsed.total == len(products)
    assert parsed.page == 1
    assert parsed.page_size == 20
    assert len(parsed.items) == len(products)

    product_item = products[0]
    parsed_item = next(i for i in parsed.items if i.id == product_item.id)

    assert parsed_item.id == product_item.id
    assert parsed_item.category_id == product_item.category_id
    assert parsed_item.name == product_item.name
    assert parsed_item.description == product_item.description
    assert Decimal(parsed_item.price) == Decimal(product_item.price)
    assert parsed_item.stock == product_item.stock
    assert parsed_item.is_active == product_item.is_active

    assert parsed_item.created_at == product_item.created_at
    assert parsed_item.created_at.tzinfo is not None


@pytest.mark.products
@pytest.mark.asyncio
async def test_get_products_filter_empty_page(client, product):

    response = await client.get(
        url=f"{base_path}/",
        params={
            "page": 9
        },
    )

    parsed = parse_product(
        response=response,
        schema=StrictProductListResponse
    )

    query_page = response.request.url.params.get("page")

    assert parsed.total == 1
    assert parsed.page == int(query_page)
    assert parsed.page_size == 20
    assert parsed.items == []

@pytest.mark.products
@pytest.mark.asyncio
async def test_get_products_filter_page_size(client, products):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "page_size": 2,
        }
    )

    parsed = parse_product(
        response=response,
        schema=StrictProductListResponse
    )

    query_page_size = int(response.request.url.params.get("page_size"))

    assert parsed.total == len(products)
    assert parsed.page == 1
    assert parsed.page_size == query_page_size
    assert len(parsed.items) == query_page_size


@pytest.mark.products
@pytest.mark.asyncio
async def test_get_products_filter_category_id(client, products):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "category_id": 2,
        }
    )

    parsed = parse_product(
        response=response,
        schema=StrictProductListResponse
       )

    query_category_id = int(response.request.url.params.get("category_id"))

    ids = [p.id for p in products if p.category_id == query_category_id]

    assert parsed.total == len(ids)
    assert parsed.page == 1
    assert parsed.page_size == 20
    if parsed.total >= parsed.page_size:
        assert len(parsed.items) == parsed.page_size
    else:
        assert len(parsed.items) == len(ids)


@pytest.mark.products
@pytest.mark.asyncio
async def test_get_products_filter_min_price(client, products):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "min_price": 2000.00,
        }
    )

    parsed = parse_product(
        response=response,
        schema=StrictProductListResponse
    )

    query_min_price = Decimal(response.request.url.params.get("min_price"))

    ids = [p.id for p in products if p.price >= query_min_price]

    assert parsed.total == len(ids)
    assert parsed.page == 1
    assert parsed.page_size == 20
    if parsed.total >= parsed.page_size:
        assert len(parsed.items) == parsed.page_size
    else:
        assert len(parsed.items) == len(ids)


@pytest.mark.products
@pytest.mark.asyncio
async def test_get_products_filter_max_price(client, products):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "max_price": 1200.00,
        }
    )

    parsed = parse_product(
        response=response,
        schema=StrictProductListResponse
    )

    query_max_price = Decimal(response.request.url.params.get("max_price"))

    ids = [p.id for p in products if p.price <= query_max_price]

    assert parsed.total == len(ids)
    assert parsed.page == 1
    assert parsed.page_size == 20
    if parsed.total >= parsed.page_size:
        assert len(parsed.items) == parsed.page_size
    else:
        assert len(parsed.items) == len(ids)

@pytest.mark.products
@pytest.mark.asyncio
async def test_get_products_filter_min_max_price(client, products):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "min_price": 1500.00,
            "max_price": 2000.00,
        }
    )

    parsed = parse_product(
        response=response,
        schema=StrictProductListResponse
    )

    query_params = response.request.url.params
    query_min_price = Decimal(query_params.get("min_price"))
    query_max_price = Decimal(query_params.get("max_price"))

    ids = [p.id for p in products if p.price >= query_min_price and p.price <= query_max_price]

    assert parsed.total == len(ids)
    assert parsed.page == 1
    assert parsed.page_size == 20
    if parsed.total >= parsed.page_size:
        assert len(parsed.items) == parsed.page_size
    else:
        assert len(parsed.items) == len(ids)

@pytest.mark.products
@pytest.mark.asyncio
async def test_get_products_filter_search(client, products):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "search": "product 2",
        }
    )

    parsed = parse_product(
        response=response,
        schema=StrictProductListResponse
    )

    query_search = str(response.request.url.params.get("search"))

    ids = [p.id for p in products if query_search in p.name]

    assert parsed.total == len(ids)
    assert parsed.page == 1
    assert parsed.page_size == 20
    if parsed.total >= parsed.page_size:
        assert len(parsed.items) == parsed.page_size
    else:
        assert len(parsed.items) == len(ids)

@pytest.mark.products
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sort_by, order",
    [
        ("price", "desc"), ("price", "asc"),
        ("name", "desc"), ("name", "asc"),
        ("created_at", "desc"), ("created_at", "asc"),
    ]
)
async def test_get_products_sorting(client, products, sort_by, order):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "sort_by": sort_by,
            "order": order,
        }
    )

    parsed = parse_product(
        response=response,
        schema=StrictProductListResponse
    )

    assert parsed.total == len(products)
    assert parsed.page == 1
    assert parsed.page_size == 20
    if parsed.total >= parsed.page_size:
        assert len(parsed.items) == parsed.page_size
    else:
        assert len(parsed.items) == len(products)

    expected_ids = [
        p.id
        for p in sorted(
            products,
            key=lambda p: (getattr(p, sort_by), p.id),
            reverse=(order == "desc")
        )
    ]

    actual_ids = [item.id for item in parsed.items]

    assert actual_ids == expected_ids

@pytest.mark.products
@pytest.mark.negative
async def test_get_product_filter_page_bellow_border(client):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "page": 0
        }
    )

    assert response.status_code == 422

@pytest.mark.products
@pytest.mark.negative
async def test_get_product_filter_invalid_page(client):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "page": "invalid-page"
        }
    )

    assert response.status_code == 422

@pytest.mark.products
@pytest.mark.negative
async def test_get_product_filter_page_size_bellow_border(client):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "page_size": 0
        }
    )

    assert response.status_code == 422

@pytest.mark.products
@pytest.mark.asyncio
async def test_get_product_filter_page_size_on_border(client, products):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "page_size": 100
        }
    )

    parsed = parse_product(
        response=response,
        schema=StrictProductListResponse
    )

    query_page_size = int(response.request.url.params.get("page_size"))

    assert parsed.total == len(products)
    assert parsed.page == 1
    assert parsed.page_size == query_page_size
    if parsed.total >= parsed.page_size:
        assert len(parsed.items) == parsed.page_size
    else:
        assert len(parsed.items) == len(products)

@pytest.mark.products
@pytest.mark.negative
async def test_get_product_filter_page_size_above_border(client):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "page_size": 101
        }
    )

    assert response.status_code == 422

@pytest.mark.products
@pytest.mark.negative
async def test_get_product_filter_invalid_page_size(client):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "page_size": "invalid-page_size"
        }
    )

    assert response.status_code == 422

@pytest.mark.products
@pytest.mark.negative
async def test_get_product_filter_category_id_bellow_border(client):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "category_id": 0
        }
    )

    assert response.status_code == 422

@pytest.mark.products
@pytest.mark.negative
async def test_get_product_filter_invalid_category_id(client):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "category_id": "invalid-category_id"
        }
    )

    assert response.status_code == 422

@pytest.mark.products
@pytest.mark.negative
async def test_get_product_filter_min_price_bellow_border(client):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "min_price": -1
        }
    )

    assert response.status_code == 422

@pytest.mark.products
@pytest.mark.asyncio
async def test_get_product_filter_min_price_on_border(client, products):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "min_price": 0
        }
    )

    parsed = parse_product(
        response=response,
        schema=StrictProductListResponse
    )

    query_min_price = Decimal(response.request.url.params.get("min_price"))

    ids = [p.id for p in products if p.price >= query_min_price]

    assert parsed.total == len(ids)
    assert parsed.page == 1
    assert parsed.page_size == 20
    if parsed.total >= parsed.page_size:
        assert len(parsed.items) == parsed.page_size
    else:
        assert len(parsed.items) == len(ids)

@pytest.mark.products
@pytest.mark.asyncio
async def test_get_product_filter_invalid_min_price(client):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "min_price": "invalid-min-price"
        }
    )

    assert response.status_code == 422

@pytest.mark.products
@pytest.mark.negative
async def test_get_product_incorrect_max_price_bellow_border(client):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "max_price": -1
        }
    )

    assert response.status_code == 422

@pytest.mark.products
@pytest.mark.asyncio
async def test_get_product_incorrect_max_price_on_border(client, products):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "max_price": 0
        }
    )

    parsed = parse_product(
        response=response,
        schema=StrictProductListResponse
    )

    query_max_price = Decimal(response.request.url.params.get("max_price"))

    ids = [p.id for p in products if p.price <= query_max_price]

    assert parsed.total == len(ids)
    assert parsed.page == 1
    assert parsed.page_size == 20
    if parsed.total >= parsed.page_size:
        assert len(parsed.items) == parsed.page_size
    else:
        assert len(parsed.items) == len(ids)

@pytest.mark.products
@pytest.mark.asyncio
async def test_get_product_filter_invalid_max_price(client):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "max_price": "invalid-min-price"
        }
    )

    assert response.status_code == 422

@pytest.mark.products
@pytest.mark.negative
async def test_get_product_filter_min_more_max(client):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "min_price": 3000,
            "max_price": 2000
        }
    )

    assert response.status_code == 422
    assert response.headers["Content-Type"].startswith("application/json")

    payload = response.json()

    detail = http_except_error_detail(payload=payload, response=response)

    assert detail["message"] == "The minimum price must be less than the maximum price"


@pytest.mark.products
@pytest.mark.negative
async def test_get_product_filter_search_bellow_lower_border(client):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "search": "",
        }
    )

    assert response.status_code == 422

@pytest.mark.products
@pytest.mark.negative
async def test_get_product_filter_search_on_lower_border(client, products):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "search": "g",
        }
    )

    parsed = parse_product(
        response=response,
        schema=StrictProductListResponse
    )

    query_search = str(response.request.url.params.get("search"))

    ids = [p.id for p in products if query_search in p.name]

    assert parsed.total == len(ids)
    assert parsed.page == 1
    assert parsed.page_size == 20
    if parsed.total >= parsed.page_size:
        assert len(parsed.items) == parsed.page_size
    else:
        assert len(parsed.items) == len(ids)

@pytest.mark.products
@pytest.mark.asyncio
async def test_get_product_filter_search_on_upper_border(client, products   ):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "search": "s"*100,
        }
    )

    parsed = parse_product(
        response=response,
        schema=StrictProductListResponse
    )

    query_search = str(response.request.url.params.get("search"))

    ids = [p.id for p in products if query_search in p.name]

    assert parsed.total == len(ids)
    assert parsed.page == 1
    assert parsed.page_size == 20
    if parsed.total >= parsed.page_size:
        assert len(parsed.items) == parsed.page_size
    else:
        assert len(parsed.items) == len(ids)

@pytest.mark.products
@pytest.mark.negative
async def test_get_product_filter_search_above_upper_border(client):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "search": "s"*101,
        }
    )
    assert response.status_code == 422


@pytest.mark.products
@pytest.mark.negative
async def test_get_product_filter_invalid_sort_by(client):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "sort_by": "invalid-sort_by",
        }
    )
    assert response.status_code == 422

@pytest.mark.products
@pytest.mark.negative
async def test_get_product_filter_invalid_order(client):
    response = await client.get(
        url=f"{base_path}/",
        params={
            "order": "invalid-order",
        }
    )
    assert response.status_code == 422