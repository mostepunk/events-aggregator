from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.adapters.db import close_mongodb, init_mongodb


@asynccontextmanager
async def startup_application(app: FastAPI):
    # startup
    await init_mongodb()
    yield
    # shutdown
    await close_mongodb()
