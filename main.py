import asyncio
from contextlib import asynccontextmanager

from pymongo import AsyncMongoClient

from app.adapters.db.cruds.event import EventCRUD
from app.adapters.schemas.events import EventCreateSchema
from app.settings import config


@asynccontextmanager
async def mongodb():
    mongodb_client = AsyncMongoClient(config.mongo.uri)
    database = mongodb_client[config.mongo.db_name]
    print(
        f"Connected to {config.mongo.host, config.mongo.port}"
        f" DB: {config.mongo.db_name}"
    )
    try:
        yield database
    # except Exception as e:
    #     print(f"MongoError: {e}")
    finally:
        await mongodb_client.close()


def event_data():
    data = {"event_type": "notification", "event_data": {"test": "new value"}}
    return EventCreateSchema(**data)


async def main():
    async with mongodb() as db:
        crud = EventCRUD(db)

        data = event_data()
        item = await crud.create(data)
        print(f"{item=}")


asyncio.run(main())
