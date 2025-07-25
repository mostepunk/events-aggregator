import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler
from typing import Any, Literal

from pydantic_settings import SettingsConfigDict

from app.settings.base import BaseSettings
from app.utils.enums import EnvironmentEnum, LogLevelEnum


class LogSettings(BaseSettings):
    """Конфигурация логирования приложения с поддержкой различных окружений.

    Обеспечивает централизованную настройку логирования для приложения и внешних библиотек,
    с возможностью различных конфигураций для локальной разработки, тестирования и продакшена.
    """

    model_config = SettingsConfigDict(env_prefix="logging_")
    app_prefix: str = "app"

    level: LogLevelEnum = LogLevelEnum.debug
    format: str = (
        "[%(asctime)s] %(levelname)-8s | %(name)-20s | %(funcName)s:%(lineno)-8d | %(message)s"
    )
    show_external: bool | None = None
    # Files section
    is_log_to_file: bool | None = None
    log_file_path: str | None = None
    file_backup_make_when: Literal[
        "S", "M", "H", "D", "W0", "W1", "W2", "W3", "W4", "W5", "W6", "midnight"
    ] = "midnight"
    file_backup_count: int = 7
    file_format: str | None = None

    def setup_logging(self):
        """Основной метод инициализации системы логирования.

        Настраивает корневой логгер, логгер приложения, внешние логгеры.
        применяет конфигурацию в зависимости от текущего окружения.
        Является точкой входа для всей системы логирования.
        """
        # sys.excepthook = self.handle_uncaught_exception
        config = self.get_logging_config()

        root_logger = logging.getLogger()
        app_logger = logging.getLogger(self.app_prefix)

        app_level = self.get_log_level(config["app_level"])
        self.setup_logger(app_logger, app_level)
        self.setup_logger(root_logger, app_level)

        external_log_level = self.get_log_level(config["external_level"])
        self.setup_external_loggers(config, external_log_level)

        logger = self.get_logger(self.__class__.__name__)
        logger.info(f"Logging configured for environment: {self.environment}")
        logger.info(f"App log level: {config['app_level']}")
        logger.info(f"External log level: {config['external_level']}")
        logger.info(f"Log to file: {config['log_to_file']}")

        if config["log_to_file"]:
            logger.info(f"Log file path: {self.log_file_path}")

    def get_logging_config(self) -> dict[str, Any]:
        """Возвращает конфигурацию логирования для текущего окружения.

        Определяет уровни логирования, настройки файлового вывода и отображения
        внешних логгеров в зависимости от среды выполнения (local/dev/prod).
        Переменные окружения имеют приоритет над дефолтными значениями.

        Returns:
            dict[str, Any]: Словарь с конфигурацией содержащий:
                - app_level: Уровень логирования для приложения
                - external_level: Уровень для внешних библиотек
                - log_to_file: Нужно ли писать в файл
                - show_external: Показывать ли логи внешних библиотек
        """
        env_configs = {
            EnvironmentEnum.local: {
                "app_level": LogLevelEnum.debug,
                "external_level": LogLevelEnum.warning,
                "log_to_file": self.is_log_to_file or False,
                "show_external": self.show_external or False,
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

    def get_logger(self, name: str) -> logging.Logger:
        """Фабрика для создания логгеров компонентов приложения.

        Создает именованный логгер с префиксом приложения. Это основной способ
        получения логгеров в сервисах и других компонентах системы.

        Args:
            name: Имя компонента (например, "EventService", "DatabaseManager")

        Returns:
            logging.Logger: Настроенный логгер с именем "{app_prefix}.{name}"
        """
        return logging.getLogger(f"{self.app_prefix}.{name}")

    def setup_logger(self, logger: logging.Logger, log_level: int) -> None:
        """Конфигурирует конкретный экземпляр логгера.

        Очищает существующие хендлеры, устанавливает уровень логирования,
        добавляет консольный хендлер и при необходимости файловый хендлер.

        Args:
            logger: Экземпляр логгера для настройки
            log_level: Числовой уровень логирования (logging.DEBUG, INFO, etc.)

        Note:
            Отключает propagation для предотвращения дублирования сообщений
        """
        config = self.get_logging_config()

        logger.handlers.clear()
        logger.setLevel(log_level)
        logger.addHandler(self.set_console_handler(log_level))
        logger.propagate = False

        if config["log_to_file"]:
            os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)

            file_handler = TimedRotatingFileHandler(
                self.log_file_path,
                when=self.file_backup_make_when,
                backupCount=self.file_backup_count,
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(self.file_formatter)

            logger.addHandler(file_handler)

    def setup_external_loggers(
        self, config: dict[str, Any], external_log_level: int
    ) -> None:
        """Настраивает логгеры внешних библиотек и зависимостей.

        Применяет конфигурацию к логгерам сторонних библиотек (urllib3, requests,
        pymongo, fastapi, etc.) для контроля их вербозности и предотвращения
        засорения логов приложения.

        Args:
            config: Конфигурация логирования из get_logging_config()
            external_log_level: Уровень логирования для внешних библиотек

        Note:
            Список библиотек можно расширять по мере добавления новых зависимостей
        """

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

        for logger_name in external_loggers:
            logger = logging.getLogger(logger_name)
            self.setup_logger(logger, external_log_level)

    def set_console_handler(self, log_level: int) -> logging.StreamHandler:
        """Создает и конфигурирует хендлер для вывода в консоль.

        Настраивает StreamHandler для stdout с применением форматтера
        и фильтра приложения. Используется как основной способ вывода логов.

        Args:
            log_level: Минимальный уровень сообщений для вывода

        Returns:
            logging.StreamHandler: Настроенный консольный хендлер
        """
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(self.formatter)
        console_handler.addFilter(self._log_filter)
        return console_handler

    def get_log_level(self, level: LogLevelEnum | None = None) -> int:
        """Конвертирует enum уровня логирования в числовое значение.

        Преобразует строковое представление уровня логирования из enum
        в числовое значение, понятное модулю logging.

        Args:
            level: Enum уровня логирования или None для использования дефолтного

        Returns:
            int: Числовое значение уровня (10=DEBUG, 20=INFO, 30=WARNING, etc.)
        """
        return getattr(logging, level or self.level, logging.INFO)

    @property
    def formatter(self):
        """Единый форматтер для всех хендлеров логгера."""
        return logging.Formatter(self.format)

    @property
    def file_formatter(self):
        """Единый форматтер для файловых хендлеров логгера."""
        return logging.Formatter(self.file_format or self.format)

    @property
    def _log_filter(self):
        """Создает фильтр для отображения только логов приложения.

        Возвращает фильтр, который пропускает только сообщения от логгеров
        с именами, начинающимися с префикса приложения. Помогает скрыть
        сообщения внешних библиотек в консоли.

        Returns:
            logging.Filter: Экземпляр фильтра для логгеров приложения

        Note:
            Создается как inner class для доступа к app_prefix
        """
        _app_prefix = self.app_prefix

        class AppLogFilter(logging.Filter):
            def filter(self, record: logging.LogRecord) -> bool:
                return record.name.startswith(_app_prefix)

        return AppLogFilter()

    def handle_uncaught_exception(self, exc_type, exc_value, exc_traceback):

        app_logger = logging.getLogger(self.app_prefix)
        app_logger.critical(
            "Uncaught exception. Application will terminate.",
            exc_info=(exc_type, exc_value, exc_traceback),
        )
