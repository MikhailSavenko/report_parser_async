import os
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from api.routers import spimex_results

load_dotenv()


scheduler = AsyncIOScheduler()


@scheduler.scheduled_job("cron", hour=14, minute=11)
async def clear_cache():
    await FastAPICache.clear()


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.from_url(os.getenv("REDIS"))
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    scheduler.start()
    yield
    await FastAPICache.clear()


app = FastAPI(lifespan=lifespan)

app.include_router(spimex_results.router)
