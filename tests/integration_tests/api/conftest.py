from httpx import ASGITransport, AsyncClient
import pytest
from api.main import app
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from sqlalchemy.ext.asyncio import AsyncSession


from .tests_data import spimex_test_data
from db.models import SpimexTradingResult


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
async def initialize_cache():
    FastAPICache.init(InMemoryBackend(), prefix="test-cache")
    yield
    await FastAPICache.clear(namespace="test-cache")


@pytest.fixture
async def fill_db_spimex_results(async_session: AsyncSession):
    for item in spimex_test_data:
        obj = SpimexTradingResult(**item)
        async_session.add(obj)
    await async_session.commit()
    yield spimex_test_data

