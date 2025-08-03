from .app_settings import AppSettings
from .base import BaseSettings
from .broker_settings import BrokerSettings
from .log_settings import LogSettings
from .mongo import MongoDBSettings


class Config(BaseSettings):
    mongo: MongoDBSettings = MongoDBSettings()
    logging: LogSettings = LogSettings()
    app: AppSettings = AppSettings()
    broker: BrokerSettings = BrokerSettings()


config = Config()
