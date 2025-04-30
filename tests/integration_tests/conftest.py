from httpx import ASGITransport, AsyncClient
import pytest
from api.main import app
from pytest_mock import MockerFixture
from fastapi_cache import decorator, FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


# @pytest.fixture
# async def fastapi_cache_mock(mocker: MockerFixture):
    
#     def no_cache(func):
#         return func
    
#     mocker.patch.object(decorator, "cache", no_cache)
#     yield


@pytest.fixture(scope="session", autouse=True)
async def initialize_cache():
    FastAPICache.init(InMemoryBackend(), prefix="test-cache")
    yield
    await FastAPICache.clear(namespace="test-cache")