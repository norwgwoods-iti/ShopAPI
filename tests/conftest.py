from decimal import Decimal

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from shopapi.core.config import settings
from shopapi.db.base import Base
from shopapi.db.session import get_session
from shopapi.main import app
from shopapi.models import CategoryModel, ProductModel

import asyncio
import sys
from collections.abc import Callable, Mapping
import pytest

""" SelectorEventLoop для Windows """
def pytest_asyncio_loop_factories(
    config: pytest.Config, item: pytest.Item
) -> Mapping[str, Callable[[], asyncio.AbstractEventLoop]]:
    if sys.platform == "win32":
        return {"selector": asyncio.SelectorEventLoop}
    return {"default": asyncio.new_event_loop}



test_engine =  create_async_engine(settings.test_database_url)

TestSession = async_sessionmaker(
    bind=test_engine,
    expire_on_commit=False,
)

async def override_get_session():
    async with TestSession() as session:
        yield session


@pytest_asyncio.fixture
async def client():
    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(autouse=True)
async def prepare_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)



@pytest_asyncio.fixture
async def db_session():
    async with TestSession() as session:
        yield session


@pytest_asyncio.fixture(
    scope="session",
    autouse=True
)
async def dispose_test_engine():
    yield
    await test_engine.dispose()


@pytest_asyncio.fixture()
async def product(db_session):
    category = CategoryModel(
        name="Test category",
        slug="test-category",
    )
    db_session.add(category)
    await db_session.flush()

    product = ProductModel(
        category_id=category.id,
        name="Test product",
        description="Product for testing",
        price=Decimal("100.00"),
        stock=10,
        is_active=True,
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)

    return product


@pytest_asyncio.fixture()
async def products(db_session):

    categories = [
        CategoryModel(
            name=f"Test category {i}",
            slug=f"test-category {i}",
        ) for i in range(1,4)
    ]

    db_session.add_all(categories)
    await db_session.flush()

    specs = [
        (categories[0], 'Test product 1', '1000.00'), # id = 1 | category_id = 1
        (categories[1], 'Test product 2', '2000.00'), # id = 2 | category_id = 2
        (categories[1], 'Test product 3', '3000.00'), # id = 3 | category_id = 2
        (categories[2], 'Test product 4', '1100.00'), # id = 4 | category_id = 1
    ]

    products = [
        ProductModel(
            category_id=category.id,
            name=name,
            description="Product for testing",
            price=Decimal(price),
            stock=10,
            is_active=True,
        ) for category, name, price in specs
    ]

    db_session.add_all(products)
    await db_session.commit()

    return products
