from datetime import datetime
from typing import Any, Optional

from bson.objectid import ObjectId
from pydantic import BaseModel, ConfigDict, Field, field_validator


def to_camel(snake_str: str) -> str:
    """автоматическое создание camelCase alias.

    _hello_world -> helloWorld

    Args:
        snake_str (str): snake_str

    Returns:
        str:
    """
    snake_str = snake_str.strip("_")
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


class BaseSchema(BaseModel):
    """BaseSchema."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        str_strip_whitespace=True,
        use_enum_values=True,
        from_attributes=True,
    )

    def json(self, exclude_unset: bool = False):
        """Schema to json.

        Args:
            exclude_unset (bool): исключить не установленные поля
        """
        return self.model_dump(mode="json", by_alias=True, exclude_unset=exclude_unset)

    def dict(self, exclude_unset: bool = False):
        """Schema to dict.

        Args:
            exclude_unset (bool): исключить не установленные поля
        """
        return self.model_dump(exclude_unset=exclude_unset)

    @field_validator("*", mode="before")
    @classmethod
    def strip_strings(cls, v: Any):
        """Убрать пробелы из строк.

        Args:
            v (Any): любое входящее значение.
        """
        if isinstance(v, str):
            return v.strip()
        return v


class BaseInsertSchemaMixin(BaseModel):
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()


class DBSchemaMixin(BaseSchema):
    id: Optional[str] = Field(default=None, alias="_id")
    created_at: datetime
    updated_at: datetime

    @field_validator("id", mode="before")
    @classmethod
    def validate_id(cls, v: ObjectId):
        if isinstance(v, ObjectId):
            return str(v)
        return v
