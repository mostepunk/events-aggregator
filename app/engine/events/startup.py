from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def startup_application(app: FastAPI):
    # startup
    yield
    # shutdown
