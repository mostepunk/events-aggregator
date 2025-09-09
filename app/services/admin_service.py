from typing import Any, Literal

from app import getLogger
from app.services.base import BaseService

logging = getLogger("AdminService")


class AdminService(BaseService):
    # TODO: покрыть тестами
    async def profiler(
        self, action: Literal["on", "off", "status"], data: dict[str, Any] = None
    ):
        logging.info(f"Profiler {action} with data: {data}")

        if action == "on":
            profiler = await self.repo.set_profiler(data)

        elif action == "off":
            data = {"level": 0}
            profiler = await self.repo.set_profiler(data)

        elif action == "status":
            profiler = await self.repo.get_profiler()

        return profiler.to_dict(verbose=True)

    async def get_raw_profiler_data(self):
        return await self.repo.get_profiler_status()
