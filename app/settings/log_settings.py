import logging
import os
import sys
from typing import Any

from pydantic_settings import SettingsConfigDict

from app.settings.base import BaseSettings
from app.utils.enums import EnvironmentEnum, LogLevelEnum


class LogSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="logging_")
    app_prefix: str = "app"

    level: LogLevelEnum = LogLevelEnum.debug
    format: str = (
        "[%(asctime)s] %(levelname)-8s | %(name)-20s | %(funcName)s:%(lineno)-8d | %(message)s"
    )
    is_log_to_file: bool | None = None
    log_file_path: str | None = None
    show_external: bool | None = None

    def get_log_level(self, level: LogLevelEnum | None = None) -> int:
        """Конвертирует строку в уровень логирования"""
        return getattr(logging, level or self.level, logging.INFO)

    def get_logging_config(self) -> dict[str, Any]:
        """Возвращает конфигурацию логирования в зависимости от среды

        Приоритет отдается переменным окружения, если они не выставлены, указываются дефолтные.
        """

        env_configs = {
            EnvironmentEnum.local: {
                "app_level": LogLevelEnum.debug,
                "external_level": LogLevelEnum.warning,
                "log_to_file": False,
                "show_external": False,
            },
            EnvironmentEnum.dev: {
                "app_level": LogLevelEnum.info,
                "external_level": LogLevelEnum.info,
                "log_to_file": self.is_log_to_file or False,
                "show_external": self.show_external or True,
            },
            EnvironmentEnum.prod: {
                "app_level": LogLevelEnum.warning,
                "external_level": LogLevelEnum.warning,
                "log_to_file": self.is_log_to_file or False,
                "show_external": self.show_external or True,
            },
        }
        return env_configs[self.environment]

    def setup_logging(self):
        """Настройка логирования для всего приложения"""
        config = self.get_logging_config()
        app_log_level = self.get_log_level(config["app_level"])
        external_log_level = self.get_log_level(config["external_level"])

        # Настраиваем корневой логгер
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.handlers.clear()

        formatter = logging.Formatter(self.format)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(app_log_level)
        console_handler.setFormatter(formatter)
        console_handler.addFilter(self._log_filter)

        # Настраиваем основной логгер приложения
        app_logger = logging.getLogger(self.app_prefix)
        app_logger.setLevel(app_log_level)
        app_logger.handlers.clear()
        app_logger.addHandler(console_handler)
        app_logger.propagate = False

        if config["log_to_file"]:
            os.makedirs(os.path.dirname(config["log_file"]), exist_ok=True)

            file_handler = logging.FileHandler(config["log_file"])
            file_handler.setLevel(app_log_level)
            file_handler.setFormatter(formatter)
            app_logger.addHandler(file_handler)

        # Настраиваем внешние логгеры
        self.setup_external_loggers(config, external_log_level)

        logger = self.get_logger(self.__class__.__name__)
        logger.info(f"Logging configured for environment: {self.environment}")
        logger.info(f"App log level: {config['app_level']}")
        logger.info(f"External log level: {config['external_level']}")
        logger.info(f"Log to file: {config['log_to_file']}")

        return app_logger

    def setup_external_loggers(
        self, config: dict[str, Any], external_log_level: int
    ) -> None:
        """Настраивает логгеры внешних библиотек"""

        external_loggers = [
            "urllib3",
            "requests",
            "httpx",
            "pymongo",
            "motor",
            "uvicorn",
            "uvicorn.access",
            "fastapi",
            "asyncio",
            "multipart",
        ]

        if (
            config["external_level"] == LogLevelEnum.notset
            or not config["show_external"]
        ):
            for logger_name in external_loggers:
                logging.getLogger(logger_name).setLevel(logging.CRITICAL + 1)
        else:
            for logger_name in external_loggers:
                logging.getLogger(logger_name).setLevel(external_log_level)

    def get_logger(self, name: str) -> logging.Logger:
        """Получить логгер с префиксом проекта

        Args:
            name: Имя компонента (например, "HealthService", "EventService")

        Returns:
            Настроенный логгер
        """
        return logging.getLogger(f"{self.app_prefix}.{name}")

    @property
    def _log_filter(self):
        """Фильтр для показа только логов нашего приложения"""
        _app_prefix = self.app_prefix

        class AppLogFilter(logging.Filter):
            def filter(self, record: logging.LogRecord) -> bool:
                return record.name.startswith(_app_prefix)

        return AppLogFilter()
