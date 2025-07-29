from fastapi import FastAPI
from starlette.responses import RedirectResponse

from app.engine.events.startup import startup_application
from app.engine.middlewares.cors_middleware import add_corse_middleware
from app.settings import config


def get_fastapi_app() -> FastAPI:
    app = FastAPI(
        **config.app.api_settings,
        lifespan=startup_application,
    )

    add_corse_middleware(app)

    @app.get("/", include_in_schema=False)
    async def docs_redirect():
        return RedirectResponse(url=config.app.prefix + config.app.doc_path)

    return app
