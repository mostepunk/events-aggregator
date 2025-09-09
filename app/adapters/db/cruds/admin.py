import asyncio
from datetime import datetime, timedelta, timezone

from pymongo.asynchronous.database import AsyncDatabase

from app import getLogger
from app.adapters.db.const import MongoCollections
from app.adapters.db.cruds.base import BaseCRUD
from app.adapters.db.utils.profiler import ProfilerState
from app.adapters.schemas.events import EventCreateSchema
from app.entities.event import Event
from app.entities.profiler import Profiler

logging = getLogger("AdminCRUD")


class AdminCRUD(BaseCRUD[EventCreateSchema, Event]):
    _in = EventCreateSchema
    _out = Event
    _table = MongoCollections.profiler_stat

    def __init__(self, db: AsyncDatabase):
        super().__init__(db)
        self.system = self.db["system.profile"]
        self.profiler_state = ProfilerState()

    async def is_profiler_enabled(self) -> bool:
        """Вернуть состояние профайлера.

        0 - Profiler is off and does not collect any data (default).
        1 - Profiler collects data for operations that exceed the slowms threshold.
        2 - Profiler collects data for all operations.
        """
        profiler = await self.get_profiler()
        return profiler.is_enabled

    async def get_profiler(self) -> Profiler:
        """Получение информации о профайлере.

        {'was': 2, 'slowms': 100, 'sampleRate': 1.0, 'ok': 1.0}
        """
        res = await self.db.command("profile", -1)
        profiler = Profiler.from_dict(res)
        self.profiler_state.update_profiler(profiler)
        return profiler

    # TODO: покрыть тестами
    async def set_profiler(self, data: dict):
        """Установить новое состояние профайлера.

        {
          "level": 2,                           # обязательный: 0/1/2
          "slowms": 100,                        # опционально для level=1
          # Взаимоисключающие параметры времени:
          "timeout_minutes": 10,                # ИЛИ минуты
          "till": "2025-08-26T14:30:00Z"        # ИЛИ точное время
        }
        """
        level = data.get("level", 1)

        additional = {}
        if slowms := data.get("slowms"):
            additional["slowms"] = slowms

        await self.db.command("profile", level, additional)
        profiler: Profiler = await self.get_profiler()

        if level == 0:
            self.profiler_state.cancel_auto_stop()
            return profiler

        await self._schedule_auto_stop(data)
        return profiler

    async def _schedule_auto_stop(self, data: dict) -> None:
        """Планирование автоотключения профайлера."""
        stop_time = None

        if till := data.get("till"):
            stop_time = till
        elif timeout_minutes := data.get("timeout_minutes"):
            stop_time = datetime.now(tz=timezone.utc) + timedelta(
                minutes=timeout_minutes
            )

        if not stop_time:
            return
        delay = (stop_time - datetime.now(tz=timezone.utc)).total_seconds()
        if delay < 0:
            return

        task = asyncio.create_task(
            self._auto_stop_after_delay(delay), name=f"Stop profiler at {stop_time}"
        )
        self.profiler_state.schedule_auto_stop(task, stop_time)

    async def _auto_stop_after_delay(self, delay_seconds: float):
        await asyncio.sleep(delay_seconds)
        await self.db.command("profile", 0)

        # Обновляем состояние после отключения
        await self.get_profiler()
        self.profiler_state.cancel_auto_stop()
        logging.info("Profiler automatically stopped")
