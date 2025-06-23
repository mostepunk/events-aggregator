from .base import BaseSettings
from .mongo import MongoDBSettings


class Config(BaseSettings):
    mongo: MongoDBSettings = MongoDBSettings()


config = Config()
