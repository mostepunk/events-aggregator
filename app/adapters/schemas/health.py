from pydantic import Field

from app.adapters.schemas.base import BaseSchema


class HealthStatusSchema(BaseSchema):
    status: str = Field(
        str,
        description="Health status: ok | error",
        example="ok",
    )
