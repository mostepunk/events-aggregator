from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.adapters.db import close_mongodb, init_mongodb
from app.adapters.db.index import init_indexes


@asynccontextmanager
async def startup_application(app: FastAPI):
    # startup
    await init_mongodb()
    await init_indexes()

    yield
    # shutdown
    await close_mongodb()
