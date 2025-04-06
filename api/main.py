from fastapi import FastAPI
from api.routers import spimex_results


app = FastAPI()


app.include_router(spimex_results.router)