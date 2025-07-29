import uvicorn

from app.settings import config

config.logging.setup_logging()


def start_server():
    uvicorn.run("app.engine.web_app:fastapi_app", **config.app.server_settings)


if __name__ == "__main__":
    start_server()
