from db.models import Base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from api.backend.db_depends import get_db
from api.main import app
import pytest_asyncio


TEST_BD_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(TEST_BD_URL)


TestingSessionLocal = async_sessionmaker(
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    bind=engine_test,
)


async def override_get_async_session():
    async with TestingSessionLocal() as async_session:
        yield async_session


app.dependency_overrides[get_db] = override_get_async_session


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def async_session():
    async with TestingSessionLocal() as session:
        yield session
