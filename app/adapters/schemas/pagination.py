from pydantic import Field

from app.adapters.schemas.base import BaseSchema


class PaginationSchema(BaseSchema):
    limit: int | None = Field(10, gt=0, example=10, description="Количество событий")
    offset: int | None = Field(
        1, ge=1, example=0, description="Смещение. Начинается с 1"
    )
