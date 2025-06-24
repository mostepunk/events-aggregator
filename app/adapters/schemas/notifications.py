"""
уведомления пользователям, вложенные статусы доставки.
"""

from app.adapters.schemas.base import BaseInsertSchemaMixin, BaseSchema


class BaseNotificationSchema(BaseSchema):
    pass


class NotificationCreateSchema(BaseInsertSchemaMixin, BaseNotificationSchema):
    pass
