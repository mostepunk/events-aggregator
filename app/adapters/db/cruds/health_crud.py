from app.adapters.db.cruds.base import BaseCRUD
from app.adapters.schemas.base import BaseSchema
from app.entities.base import BaseEntity

IN = BaseSchema
OUT = BaseEntity
TABLE = "health"


class HealthCRUD(BaseCRUD[IN, OUT]):
    _in = None
    _out = None
    _table = TABLE

    async def ping(self):
        res = await self.db.command("ping")
        return res

    async def server_status(self):
        res = await self.db.command("serverStatus")
        return res
