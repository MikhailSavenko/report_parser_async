import pytest_asyncio
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from api.main import app
from db.models import SpimexTradingResult

from .tests_data import spimex_test_data


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture(scope="session", autouse=True)
async def initialize_cache():
    FastAPICache.init(InMemoryBackend(), prefix="test-cache")
    yield
    await FastAPICache.clear(namespace="test-cache")


@pytest_asyncio.fixture
async def fill_db_spimex_results(async_session: AsyncSession):
    """Наполняем базу данными из test_data.py"""

    for item in spimex_test_data:
        obj = SpimexTradingResult(**item)
        async_session.add(obj)

    await async_session.commit()

    yield spimex_test_data

    await async_session.execute(delete(SpimexTradingResult))
    await async_session.commit()
