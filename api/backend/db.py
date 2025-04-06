from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from dotenv import load_dotenv
import os



load_dotenv()

DATABASE_URL = os.getenv("ADATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True)


async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

