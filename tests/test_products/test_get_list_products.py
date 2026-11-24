from calendar import prcal
from datetime import datetime
from decimal import Decimal
from typing import Any

import pytest
from httpx import AsyncClient

from tests.schemas import StrictProductListResponse
from tests.utils import parse_response_schema, parse_error_detail, parse_system_error_detail

base_path = "/api/v1/products"

@pytest.mark.get_products
async def test_get_products_response_contract(
        auth_client: AsyncClient,
        products
):
    response = await auth_client.get(
        url=f"{base_path}/",
    )
    parsed = parse_response_schema(
        response=response,
        schema=StrictProductListResponse,
        status_code=200
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


@pytest.mark.get_products
async def test_get_products_price_keeps_two_decimals(
        auth_client: AsyncClient,
        products
):
    response = await auth_client.get(
        url=f"{base_path}/",
    )
    parsed = parse_response_schema(
        response=response,
        schema=StrictProductListResponse,
        status_code=200
    )
    for item in parsed.items:
        assert item.price.as_tuple().exponent == -2


@pytest.mark.update_product
async def test_get_product_datetime_is_aware(
        auth_client: AsyncClient,
        products
):
    response = await auth_client.get(
        url=f"{base_path}/",
    )
    parsed = parse_response_schema(
        response=response,
        schema=StrictProductListResponse,
        status_code=200
    )
    for item in parsed.items:
        assert item.created_at.tzinfo is not None


@pytest.mark.get_products
async def test_get_one_product_success(
        auth_client: AsyncClient,
        product
):
    response = await auth_client.get(
        url=f"{base_path}/",
    )
    parsed = parse_response_schema(
        response=response,
        schema=StrictProductListResponse,
        status_code=200
    )
    assert parsed.total == 1
    assert parsed.page == 1
    assert parsed.page_size == 20
    assert len(parsed.items) == parsed.total

    for item in parsed.items:
        assert item.id == product.id
        assert item.category_id == product.category_id
        assert item.name == product.name
        assert item.description == product.description
        assert Decimal(item.price) == Decimal(product.price)
        assert item.stock == product.stock
        assert item.is_active == product.is_active


@pytest.mark.get_products
async def test_get_products_success(
        auth_client: AsyncClient,
        products
):
    response = await auth_client.get(
        url=f"{base_path}/",
    )
    parsed = parse_response_schema(
        response=response,
        schema=StrictProductListResponse,
        status_code=200
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


@pytest.mark.get_products
async def test_check_get_hide_product(
        auth_client: AsyncClient,
        products,
        product,
        db_session
):
    setattr(product, "is_active", False)
    await db_session.commit()

    response = await auth_client.get(
        url=f"{base_path}/"
    )
    parsed = parse_response_schema(
        response=response,
        schema=StrictProductListResponse,
        status_code=200
    )
    expected_ids = [p.id for p in products]
    actual_ids = [p.id for p in parsed.items]

    assert set(actual_ids) == set(expected_ids)


@pytest.mark.get_products
async def test_get_products_filter_empty_page(
        auth_client: AsyncClient,
        product
):
    response = await auth_client.get(
        url=f"{base_path}/",
        params={
            "page": 9
        },
    )
    parsed = parse_response_schema(
        response=response,
        schema=StrictProductListResponse,
        status_code=200
    )
    query_page = response.request.url.params.get("page")

    assert parsed.total == 1
    assert parsed.page == int(query_page)
    assert parsed.page_size == 20
    assert parsed.items == []


@pytest.mark.get_products
async def test_get_products_filter_page_size(
        auth_client: AsyncClient,
        products
):
    response = await auth_client.get(
        url=f"{base_path}/",
        params={
            "page_size": 2,
        }
    )
    parsed = parse_response_schema(
        response=response,
        schema=StrictProductListResponse,
        status_code=200
    )
    query_page_size = int(response.request.url.params.get("page_size"))

    assert parsed.total == len(products)
    assert parsed.page == 1
    assert parsed.page_size == query_page_size
    if len(products) >= query_page_size:
        assert len(parsed.items) == query_page_size
    else:
        assert len(parsed.items) == len(products)


@pytest.mark.get_products
async def test_get_products_filter_page_have_product(
        auth_client: AsyncClient,
        products
):
    query_params = {
        "page": 2,
        "page_size": 2,
    }
    response = await auth_client.get(
        url=f"{base_path}/",
        params=query_params
    )
    parsed = parse_response_schema(
        response=response,
        schema=StrictProductListResponse,
        status_code=200
    )
    query_params = response.request.url.params
    query_page = int(query_params.get("page"))
    query_page_size = int(query_params.get("page_size"))

    assert parsed.total == len(products)
    assert parsed.page == query_page
    assert parsed.page_size == query_page_size

    if parsed.total >= query_page_size:
        assert len(parsed.items) == query_page_size
    else:
        assert len(parsed.items) == len(products)


@pytest.mark.get_products
async def test_get_products_filter_category_id(
        auth_client: AsyncClient,
        products
):
    expend_category_id = products[1].category_id

    response = await auth_client.get(
        url=f"{base_path}/",
        params={
            "category_id": expend_category_id,
        }
    )
    parsed = parse_response_schema(
        response=response,
        schema=StrictProductListResponse,
        status_code=200
       )
    query_category_id = int(response.request.url.params.get("category_id"))

    expected_ids = [p.id for p in products if p.category_id == query_category_id]
    actual_ids = [item.id for item in parsed.items]
    assert set(actual_ids) == set(expected_ids)

    assert parsed.total == len(expected_ids)
    assert parsed.page == 1
    assert parsed.page_size == 20
    if parsed.total >= parsed.page_size:
        assert len(parsed.items) == parsed.page_size
    else:
        assert len(parsed.items) == len(expected_ids)


@pytest.mark.get_products
async def test_get_products_filter_min_price(
        auth_client: AsyncClient,
        products
):
    response = await auth_client.get(
        url=f"{base_path}/",
        params={
            "min_price": 2000.00,
        }
    )
    parsed = parse_response_schema(
        response=response,
        schema=StrictProductListResponse,
        status_code=200
    )
    query_min_price = Decimal(response.request.url.params.get("min_price"))

    expected_ids = [p.id for p in products if p.price >= query_min_price]
    actual_ids = [item.id for item in parsed.items]
    assert set(actual_ids) == set(expected_ids)

    assert parsed.total == len(expected_ids)
    assert parsed.page == 1
    assert parsed.page_size == 20
    if parsed.total >= parsed.page_size:
        assert len(parsed.items) == parsed.page_size
    else:
        assert len(parsed.items) == len(expected_ids)


@pytest.mark.get_products
async def test_get_products_filter_max_price(
        auth_client: AsyncClient,
        products
):
    response = await auth_client.get(
        url=f"{base_path}/",
        params={
            "max_price": 1200.00,
        }
    )
    parsed = parse_response_schema(
        response=response,
        schema=StrictProductListResponse,
        status_code=200
    )
    query_max_price = Decimal(response.request.url.params.get("max_price"))

    expected_ids = [p.id for p in products if p.price <= query_max_price]
    actual_ids = [item.id for item in parsed.items]
    assert set(actual_ids) == set(expected_ids)

    assert parsed.total == len(expected_ids)
    assert parsed.page == 1
    assert parsed.page_size == 20
    if parsed.total >= parsed.page_size:
        assert len(parsed.items) == parsed.page_size
    else:
        assert len(parsed.items) == len(expected_ids)


@pytest.mark.get_products
async def test_get_products_filter_min_max_price(
        auth_client: AsyncClient,
        products
):
    query_params = {
        "min_price": 1500.00,
        "max_price": 2000.00,
    }
    response = await auth_client.get(
        url=f"{base_path}/",
        params=query_params
    )
    parsed = parse_response_schema(
        response=response,
        schema=StrictProductListResponse,
        status_code=200
    )
    query_params = response.request.url.params
    query_min_price = Decimal(query_params.get("min_price"))
    query_max_price = Decimal(query_params.get("max_price"))

    expected_ids = [
        p.id for p in products
        if p.price >= query_min_price
           and p.price <= query_max_price
    ]
    actual_ids = [item.id for item in parsed.items]
    assert set(actual_ids) == set(expected_ids)

    assert parsed.total == len(expected_ids)
    assert parsed.page == 1
    assert parsed.page_size == 20
    if parsed.total >= parsed.page_size:
        assert len(parsed.items) == parsed.page_size
    else:
        assert len(parsed.items) == len(expected_ids)


@pytest.mark.get_products
@pytest.mark.parametrize(
    "sort_by, order",
    [
        ("price", "desc"), ("price", "asc"),
        ("name", "desc"), ("name", "asc"),
        ("created_at", "desc"), ("created_at", "asc"),
    ]
)
async def test_get_products_sorting(
        auth_client: AsyncClient,
        products
        , sort_by, order):
    query_params = {
        "sort_by": sort_by,
        "order": order,
    }
    response = await auth_client.get(
        url=f"{base_path}/",
        params=query_params
    )
    parsed = parse_response_schema(
        response=response,
        schema=StrictProductListResponse,
        status_code=200
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


""" Check Field category_id/page/page_size """
@pytest.mark.get_products
@pytest.mark.negative
@pytest.mark.parametrize(
    "query_name, query_value", [

        pytest.param("category_id", 1.5, id="category_id-float-value"),
        pytest.param("category_id", "test!@#", id="category_id-string-value"),
        pytest.param("category_id", "", id="category_id-empty-str-value"),
        pytest.param("category_id", "   ", id="category_id-whitespace-only-value"),
        pytest.param("category_id", True, id="category_id-boolean-value"),
        pytest.param("category_id", None, id="category_id-None-value"),
        pytest.param("category_id", "null", id="category_id-json-null-value"),
        pytest.param("category_id", {}, id="category_id-dict-value"),

        pytest.param("page", 1.5, id="page-float-value"),
        pytest.param("page", "test!@#", id="page-string-value"),
        pytest.param("page", "", id="page-empty-str-value"),
        pytest.param("page", "   ", id="page-whitespace-only-value"),
        pytest.param("page", True, id="page-boolean-value"),
        pytest.param("page", None, id="page-None-value"),
        pytest.param("page", "null", id="page-json-null-value"),
        pytest.param("page", {}, id="page-dict-value"),

        pytest.param("page_size", 1.5, id="page_size-float-value"),
        pytest.param("page_size", "test!@#", id="page_size-string-value"),
        pytest.param("page_size", "", id="page_size-empty-str-value"),
        pytest.param("page_size", "   ", id="page_size-whitespace-only-value"),
        pytest.param("page_size", True, id="page_size-boolean-value"),
        pytest.param("page_size", None, id="page_size-None-value"),
        pytest.param("page_size", "null", id="page_size-json-null-value"),
        pytest.param("page_size", {}, id="page_size-dict-value"),
    ]
)
async def test_get_product_filter_field_category_page_psize_types(
        auth_client: AsyncClient,
        products,
        query_name:Any,
        query_value:Any
):
    response = await auth_client.get(
        url=f"{base_path}/",
        params={
            query_name: query_value
        }
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="Input should be a valid integer, unable to parse string as an integer",
    )


@pytest.mark.get_products
@pytest.mark.negative
@pytest.mark.parametrize(
    "query_name, query_value", [

            pytest.param("category_id", 0, id="category_id-zero-value"),
            pytest.param("category_id", -1, id="category_id-negative-value"),

            pytest.param("page", 0, id="page-zero-value"),
            pytest.param("page", -1, id="page-negative-value"),

            pytest.param("page_size", 0, id="page_size-zero-value"),
            pytest.param("page_size", -1, id="page_size-negative-value"),

    ]
)
async def test_get_products_filter_category_page_psize_under_min_value(
        auth_client: AsyncClient,
        products,
        query_name:str,
        query_value:int
):
    response = await auth_client.get(
        url=f"{base_path}/",
        params={
            query_name: query_value
        }
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="Input should be greater than or equal to 1",
    )


""" Check Field category_id """
@pytest.mark.get_products
@pytest.mark.negative
async def test_get_products_filter_incorrect_category_id(
        auth_client: AsyncClient,
        products
):
    response = await auth_client.get(
        url=f"{base_path}/",
        params={
            "category_id": 9999999
        }
    )
    parsed = parse_response_schema(
        response=response,
        schema=StrictProductListResponse,
        status_code=200
    )
    for item in parsed.items:
        assert item is None


""" Check Field page_size """
@pytest.mark.get_products
async def test_get_product_filter_page_size_max(
        auth_client: AsyncClient,
        products
):
    response = await auth_client.get(
        url=f"{base_path}/",
        params={
            "page_size": 100
        }
    )
    parsed = parse_response_schema(
        response=response,
        schema=StrictProductListResponse,
        status_code=200
    )
    query_page_size = int(response.request.url.params.get("page_size"))

    assert parsed.total == len(products)
    assert parsed.page == 1
    assert parsed.page_size == query_page_size
    if parsed.total >= parsed.page_size:
        assert len(parsed.items) == parsed.page_size
    else:
        assert len(parsed.items) == len(products)


@pytest.mark.get_products
@pytest.mark.negative
async def test_get_product_filter_page_size_exceeds_max(auth_client):
    response = await auth_client.get(
        url=f"{base_path}/",
        params={
            "page_size": 101
        }
    )
    assert response.status_code == 422


""" Check Field min_price/max_price """
@pytest.mark.get_products
@pytest.mark.negative
@pytest.mark.parametrize(
    "query_name, query_value", [

        pytest.param("min_price", "test!@#", id="min_price-string-value"),
        pytest.param("min_price", "", id="min_price-empty-str-value"),
        pytest.param("min_price", "   ", id="min_price-whitespace-only-value"),
        pytest.param("min_price", True, id="min_price-boolean-value"),
        pytest.param("min_price", None, id="min_price-None-value"),
        pytest.param("min_price", "null", id="min_price-json-null-value"),
        pytest.param("min_price", {}, id="min_price-dict-value"),

        pytest.param("max_price", "test!@#", id="max_price-string-value"),
        pytest.param("max_price", "", id="max_price-empty-str-value"),
        pytest.param("max_price", "   ", id="max_price-whitespace-only-value"),
        pytest.param("max_price", True, id="max_price-boolean-value"),
        pytest.param("max_price", None, id="max_price-None-value"),
        pytest.param("max_price", "null", id="max_price-json-null-value"),
        pytest.param("max_price", {}, id="max_price-dict-value"),

    ]
)
async def test_get_product_filter_field_min_max_price_types(
        auth_client: AsyncClient,
        products,
        query_name:Any,
        query_value:Any
):
    response = await auth_client.get(
        url=f"{base_path}/",
        params={
            query_name: query_value
        }
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="Input should be a valid decimal"
    )


@pytest.mark.get_products
@pytest.mark.negative
@pytest.mark.parametrize(
    "query_name, query_value", [

            pytest.param("min_price", -1, id="min_price-negative-value"),

            pytest.param("max_price", -1, id="max_price-negative-value"),
    ]
)
async def test_get_products_filter_price_under_min_value(
        auth_client: AsyncClient,
        products,
        query_name:str,
        query_value:int
):
    response = await auth_client.get(
        url=f"{base_path}/",
        params={
            query_name: query_value
        }
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="Input should be greater than or equal to 0",
    )

@pytest.mark.get_products
@pytest.mark.negative
async def test_get_product_filter_min_more_max_price(auth_client):
    query_params={
        "min_price": 3000.00,
        "max_price": 2000.00
    }
    response = await auth_client.get(
        url=f"{base_path}/",
        params=query_params
    )
    parse_error_detail(
        response=response,
        expected_status_code=422,
        message_error="The minimum price must be less than the maximum price"
    )


@pytest.mark.get_products
async def test_get_product_filter_min_equal_max_price(
        auth_client: AsyncClient,
        products
):
    query_params={
        "min_price": 2000.00,
        "max_price": 2000.00
    }
    response = await auth_client.get(
        url=f"{base_path}/",
        params=query_params
    )
    parsed = parse_response_schema(
        response=response,
        schema=StrictProductListResponse,
        status_code=200
    )
    expected_ids = [
        p.id for p in products
        if p.price == query_params["min_price"] and p.price == query_params["max_price"]
    ]
    actual_ids = [item.id for item in parsed.items]

    assert set(actual_ids) == set(expected_ids)


""" Check Field min_price """
@pytest.mark.get_products
async def test_get_product_filter_min_price_min_value(
        auth_client: AsyncClient,
        products
):
    response = await auth_client.get(
        url=f"{base_path}/",
        params={
            "min_price": 0.00
        }
    )
    parsed = parse_response_schema(
        response=response,
        schema=StrictProductListResponse,
        status_code=200
    )
    query_min_price = Decimal(response.request.url.params.get("min_price"))

    expected_ids = [p.id for p in products if p.price >= query_min_price]
    actual_ids = [p.id for p in parsed.items]
    assert set(actual_ids) == set(expected_ids)

    assert parsed.total == len(expected_ids)
    assert parsed.page == 1
    assert parsed.page_size == 20
    if parsed.total >= parsed.page_size:
        assert len(parsed.items) == parsed.page_size
    else:
        assert len(parsed.items) == len(expected_ids)


""" Check Field max_price """
@pytest.mark.get_products
async def test_get_product_max_price_min_value(
        auth_client: AsyncClient,
        products
):
    response = await auth_client.get(
        url=f"{base_path}/",
        params={
            "max_price": 0.00
        }
    )
    parsed = parse_response_schema(
        response=response,
        schema=StrictProductListResponse,
        status_code=200
    )
    query_max_price = Decimal(response.request.url.params.get("max_price"))

    expected_ids = [p.id for p in products if p.price <= query_max_price]
    actual_ids = [p.id for p in parsed.items]
    assert set(actual_ids) == set(expected_ids)

    assert parsed.total == len(expected_ids)
    assert parsed.page == 1
    assert parsed.page_size == 20
    if parsed.total >= parsed.page_size:
        assert len(parsed.items) == parsed.page_size
    else:
        assert len(parsed.items) == len(expected_ids)


""" Test Field search """
@pytest.mark.get_products
async def test_get_products_filter_search(
        auth_client: AsyncClient,
        products
):
    name_product = products[1].name
    search_name = name_product.lower().lstrip('test ') # "product 2"
    response = await auth_client.get(
        url=f"{base_path}/",
        params={
            "search": search_name,
        }
    )
    parsed = parse_response_schema(
        response=response,
        schema=StrictProductListResponse,
        status_code=200
    )
    expected_ids = [
        p.id for p in products
        if search_name in p.name
    ]
    actual_ids = [item.id for item in parsed.items]
    assert set(actual_ids) == set(expected_ids)

    assert parsed.total == len(expected_ids)
    assert parsed.page == 1
    assert parsed.page_size == 20
    if parsed.total >= parsed.page_size:
        assert len(parsed.items) == parsed.page_size
    else:
        assert len(parsed.items) == len(expected_ids)


@pytest.mark.get_products
async def test_get_products_filter_search_uppercase(
        auth_client: AsyncClient,
        products
):
    name_product = products[1].name
    search_name = name_product.lower().lstrip('test ')  # "product 2"
    response = await auth_client.get(
        url=f"{base_path}/",
        params={
            "search": search_name.upper(), # "PRODUCT 2"
        }
    )
    parsed = parse_response_schema(
        response=response,
        schema=StrictProductListResponse,
        status_code=200
    )
    query_search = str(response.request.url.params.get('search').lower().strip())
    expected_ids = [
        p.id for p in products
        if query_search in p.name
    ]
    actual_ids = [item.id for item in parsed.items]
    assert set(actual_ids) == set(expected_ids)


@pytest.mark.get_products
async def test_get_products_filter_search_space_around(
        auth_client: AsyncClient,
        products
):
    name_product = products[1].name
    search_name = name_product.lower().lstrip('test ')  # "product 2"
    response = await auth_client.get(
        url=f"{base_path}/",
        params={
            "search": f" {search_name} ", # " product 2 "
        }
    )
    parsed = parse_response_schema(
        response=response,
        schema=StrictProductListResponse,
        status_code=200
    )
    query_search = str(response.request.url.params.get('search').lower().strip())
    expected_ids = [
        p.id for p in products
        if query_search in p.name
    ]
    actual_ids = [item.id for item in parsed.items]
    assert set(actual_ids) == set(expected_ids)


@pytest.mark.get_products
@pytest.mark.negative
@pytest.mark.parametrize(
    "search", [
        pytest.param("", id="category_id-empty-str-value"),
        pytest.param(None, id="category_id-None-value"),
    ]
)
async def test_get_product_filter_search_invalid_types(
        auth_client: AsyncClient,
        products,
        search: Any
):
    response = await auth_client.get(
        url=f"{base_path}/",
        params={
            "search": search
        }
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="String should have at least 1 character",
    )


@pytest.mark.get_products
@pytest.mark.negative
async def test_get_product_filter_search_min_value(
        auth_client: AsyncClient,
        products
):
    response = await auth_client.get(
        url=f"{base_path}/",
        params={
            "search": "g",
        }
    )
    parsed = parse_response_schema(
        response=response,
        schema=StrictProductListResponse,
        status_code=200
    )
    query_search = str(response.request.url.params.get("search"))

    expected_ids = [p.id for p in products if query_search.lower() in p.name.lower()]
    actual_ids = [p.id for p in parsed.items]
    assert set(actual_ids) == set(expected_ids)

    assert parsed.total == len(expected_ids)
    assert parsed.page == 1
    assert parsed.page_size == 20
    if parsed.total >= parsed.page_size:
        assert len(parsed.items) == parsed.page_size
    else:
        assert len(parsed.items) == len(expected_ids)


@pytest.mark.get_products
async def test_get_product_filter_search_max_value(
        auth_client: AsyncClient,
        products
):
    response = await auth_client.get(
        url=f"{base_path}/",
        params={
            "search": "s"*100,
        }
    )
    parsed = parse_response_schema(
        response=response,
        schema=StrictProductListResponse,
        status_code=200
    )
    query_search = str(response.request.url.params.get("search"))

    expected_ids = [p.id for p in products if query_search in p.name]
    actual_ids = [p.id for p in parsed.items]
    assert set(actual_ids) == set(expected_ids)

    assert parsed.total == len(expected_ids)
    assert parsed.page == 1
    assert parsed.page_size == 20
    if parsed.total >= parsed.page_size:
        assert len(parsed.items) == parsed.page_size
    else:
        assert len(parsed.items) == len(expected_ids)


@pytest.mark.get_products
@pytest.mark.negative
async def test_get_product_filter_search_exceeds_max_value(
        auth_client: AsyncClient,
        products
):
    response = await auth_client.get(
        url=f"{base_path}/",
        params={
            "search": "s"*101,
        }
    )
    assert response.status_code == 422


@pytest.mark.get_products
@pytest.mark.negative
@pytest.mark.parametrize(
    "sort_by", [

        pytest.param(15, id="category_id-float-alue"),
        pytest.param(1.5, id="category_id-float-value"),
        pytest.param("test!@#", id="category_id-string-value"),
        pytest.param("", id="category_id-empty-str-value"),
        pytest.param("   ", id="category_id-whitespace-only-value"),
        pytest.param(True, id="category_id-boolean-value"),
        pytest.param(None, id="category_id-None-value"),
        pytest.param("null", id="category_id-json-null-value"),
        pytest.param({}, id="category_id-dict-value"),

    ]
)
async def test_get_product_filter_sort_by_invalid_types(
        auth_client: AsyncClient,
        products,
        sort_by: Any,
):
    response = await auth_client.get(
        url=f"{base_path}/",
        params={
            "sort_by": sort_by
        }
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="Input should be 'price', 'name' or 'created_at'",
    )


@pytest.mark.get_products
@pytest.mark.parametrize(
    "order", [
        "desc", "asc"
    ]
)
async def test_get_product_filter_sort_by_same_price(
        auth_client: AsyncClient,
        products,
        order,
):
    response = await auth_client.get(
        url=f"{base_path}/",
        params={
            "sort_by": "price",
            "order": order,
        }
    )
    parsed = parse_response_schema(
        response=response,
        schema=StrictProductListResponse,
        status_code=200
    )
    expected_ids = [
        p.id
        for p in sorted(
            products,
            key=lambda p: (getattr(p, "price"), p.id),
            reverse=(order == "desc")
        )
    ]
    actual_ids = [p.id for p in parsed.items]
    assert set(actual_ids) == set(expected_ids)


@pytest.mark.get_products
@pytest.mark.parametrize(
    "order", [
        "desc", "asc"
    ]
)
async def test_get_product_filter_sort_by_same_name(
        auth_client: AsyncClient,
        products,
        order,
):
    response = await auth_client.get(
        url=f"{base_path}/",
        params={
            "sort_by": "name",
            "order": order,
        }
    )
    parsed = parse_response_schema(
        response=response,
        schema=StrictProductListResponse,
        status_code=200
    )
    expected_ids = [
        p.id
        for p in sorted(
            products,
            key=lambda p: (getattr(p, "name"), p.id),
            reverse=(order == "desc")
        )
    ]
    actual_ids = [p.id for p in parsed.items]
    assert set(actual_ids) == set(expected_ids)


@pytest.mark.get_products
@pytest.mark.negative
@pytest.mark.parametrize(
    "order", [

        pytest.param(15, id="category_id-float-alue"),
        pytest.param(1.5, id="category_id-float-value"),
        pytest.param("test!@#", id="category_id-string-value"),
        pytest.param("", id="category_id-empty-str-value"),
        pytest.param("   ", id="category_id-whitespace-only-value"),
        pytest.param(True, id="category_id-boolean-value"),
        pytest.param(None, id="category_id-None-value"),
        pytest.param("null", id="category_id-json-null-value"),
        pytest.param({}, id="category_id-dict-value"),

    ]
)
async def test_get_product_filter_order_invalid_types(
        auth_client: AsyncClient,
        products,
        order: Any,
):
    response = await auth_client.get(
        url=f"{base_path}/",
        params={
            "order": order
        }
    )
    parse_system_error_detail(
        response=response,
        expected_status_code=422,
        message_error="Input should be 'desc' or 'asc'",
    )


""" Authorization Check """
@pytest.mark.get_products
@pytest.mark.negative
async def test_get_product_unauthorized(
        client: AsyncClient,
        products
):
    response = await client.get(
        url=f"{base_path}/",
    )
    parse_error_detail(
        response=response,
        expected_status_code=401,
        message_error="Not authenticated"
    )


@pytest.mark.get_products
@pytest.mark.negative
async def test_get_product_invalid_token(
        client: AsyncClient,
        products
):
    response = await client.get(
        url=f"{base_path}/",
        headers={
            "Authorization": "invalid-token",
        }
    )
    parse_error_detail(
        response=response,
        expected_status_code=401,
        message_error="Not authenticated"
    )


@pytest.mark.get_products
async def test_get_product_admin_token(
        admin_client: AsyncClient,
        products
):
    response = await admin_client.get(
        url=f"{base_path}/",
    )
    parse_response_schema(
        response=response,
        schema=StrictProductListResponse,
        status_code=200
    )