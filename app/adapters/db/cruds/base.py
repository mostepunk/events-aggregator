from typing import Any, Generic, TypeVar

from bson.objectid import ObjectId
from pymongo.asynchronous.database import AsyncDatabase

from app.adapters.schemas.base import BaseSchema

S_in = TypeVar("S_in", bound=BaseSchema)
S_out = TypeVar("S_out", bound=BaseSchema)
T = TypeVar("T", bound=str)


class BaseCRUD(Generic[S_in, S_out, T]):
    _in_schema: type[S_in]
    _out_schema: type[S_out]
    _table: type[T]

    def __init__(self, db: AsyncDatabase):
        self.db = db
        self.table = self.db[self._table]

    async def create(self, data: S_in | dict[str, Any]) -> S_out:
        if isinstance(data, self._in_schema):
            data = data.dict()
        item = await self.table.insert_one(data)
        return self._out_schema.model_validate(await self.get_by_id(item.inserted_id))

    async def get_by_id(self, item_id: str | ObjectId):
        item_id = self.convert_id_to_ObjectId(item_id)
        return await self.table.find_one({"_id": item_id})

    async def get_all(self, limit=10):
        return await self.table.find(limit=limit)

    async def update(self, item_id, data):
        item_id = self.convert_id_to_ObjectId(item_id)
        return await self.table.update_one({"_id": item_id}, {"$set": data})

    async def delete(self, item_id):
        item_id = self.convert_id_to_ObjectId(item_id)
        return await self.table.delete_one({"_id": item_id})

    @staticmethod
    def convert_id_to_ObjectId(item_id):
        if isinstance(item_id, str):
            return ObjectId(item_id)
        return item_id
