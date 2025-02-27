import asyncio
import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .models import Base

load_dotenv()

DATABASE_URL = os.getenv("ADATABASE_URL")

engine = create_async_engine(DATABASE_URL)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(create_tables())
