from app.adapters.schemas.base import BaseSchema
from app.utils.enums import NotificationTypeEnum


class NotificationSchema(BaseSchema):
    type: NotificationTypeEnum = NotificationTypeEnum.email
    message: str
    params: dict
