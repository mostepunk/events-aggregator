import asyncio

from faststream.redis.fastapi import RedisBroker

from app.settings import config
from app.utils.data_generator import event_streamer


async def main():
    broker = RedisBroker(config.broker.uri.get_secret_value())
    await broker.connect()

    for event in event_streamer():
        await broker.publish(event, "events-channel")


if __name__ == "__main__":
    asyncio.run(main())
