import asyncio
from datetime import datetime
from typing import Optional

from app import getLogger
from app.entities.profiler import Profiler

logging = getLogger("ProfilerState")


class ProfilerState:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._profiler = None
            cls._instance._auto_stop_task = None
            cls._instance._task_name = None
            cls._instance._scheduled_stop_time = None
        return cls._instance

    @property
    def profiler(self) -> Optional[Profiler]:
        return self._profiler

    @property
    def task_name(self) -> str:
        if self._auto_stop_task:
            return self._auto_stop_task.get_name()
        return "<no task>"

    @property
    def scheduled_stop_time(self) -> Optional[datetime]:
        return self._scheduled_stop_time

    @property
    def has_scheduled_stop(self) -> bool:
        return self._scheduled_stop_time is not None

    def update_profiler(self, profiler: Profiler):
        """Обновляет текущее состояние профайлера"""
        self._profiler = profiler
        self._profiler.stop_time = self.scheduled_stop_time

    def schedule_auto_stop(self, task: asyncio.Task, stop_time: datetime):
        """Планирует автоостановку"""
        self.cancel_auto_stop()
        self._auto_stop_task = task
        self._scheduled_stop_time = stop_time
        self._profiler.stop_time = stop_time
        logging.debug(f"Scheduled new task: <{self.task_name}>")

    def cancel_auto_stop(self):
        """Отменяет запланированную автоостановку"""
        if self._auto_stop_task and not self._auto_stop_task.done():
            self._auto_stop_task.cancel()
            logging.debug(f"Cancelled task: <{self.task_name}>")
        self._auto_stop_task = None
        self._scheduled_stop_time = None

        if self._profiler:
            self._profiler.stop_time = None
