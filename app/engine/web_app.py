from app.api.asyncapi import async_api_router
from app.api.rest import main_router
from app.engine.constructor import get_fastapi_app

fastapi_app = get_fastapi_app()
fastapi_app.include_router(main_router)
fastapi_app.include_router(async_api_router)
