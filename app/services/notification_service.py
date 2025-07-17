from typing import Any

from app.adapters.db.cruds.base import BaseCRUD
from app.services.base import BaseService


class NotificationService(BaseService):
    def __init__(self, repository: BaseCRUD):
        super().__init__(repository)

    async def notify(self, params: dict[str, Any]):
        """Отправить уведомление в очередь брокера сообщений"""
        pass
