from pydantic import Field

from app.adapters.schemas.base import BaseSchema


class PaginationSchema(BaseSchema):
    limit: int | None = Field(None, gt=0, example=10, description="Количество событий")
    offset: int | None = Field(
        None, ge=1, example=0, description="Смещение. Начинается с 1"
    )
