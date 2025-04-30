from db.models import Base
from sqlalchemy.ext.asyncio import create_async_engine
import pytest

TEST_BD_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(TEST_BD_URL)


@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
