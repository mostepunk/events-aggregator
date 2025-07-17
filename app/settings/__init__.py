from .base import BaseSettings
from .log_settings import LogSettings
from .mongo import MongoDBSettings


class Config(BaseSettings):
    mongo: MongoDBSettings = MongoDBSettings()
    logging: LogSettings = LogSettings()


config = Config()
