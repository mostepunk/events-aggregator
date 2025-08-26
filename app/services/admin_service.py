import random
from typing import Any, Literal

from app import getLogger
from app.services.base import BaseService

logging = getLogger("AdminService")


class AdminService(BaseService):
    def __init__(self, repository):
        super().__init__(repository)

    async def profiler(
        self, action: Literal["on", "off", "status"], data: dict[str, Any] = None
    ):
        logging.info(f"Profiler {action} with data: {data}")
        if action == "on":
            return {"status": "Profiler turrned on"}

        elif action == "off":
            return {"status": "Profiler turrned off"}

        elif action == "status":
            return {
                "status": random.choice(
                    [
                        "Profiler turrned on",
                        "Profiler turrned off",
                    ]
                )
            }

    async def get_raw_profiler_data(self):
        pass
