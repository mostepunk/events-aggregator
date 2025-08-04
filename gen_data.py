import asyncio

from faststream.redis.fastapi import RedisBroker

from app.settings import config
from app.utils.data_generator import event_streamer


async def main():
    broker = RedisBroker(config.broker.uri.get_secret_value())
    await broker.connect()

    for event in event_streamer():
        print(
            f"Создано событие. Тип: {event.get('type')}. "
            f"Критичность: {event.get('severity')}"
        )
        await broker.publish(event, "events-channel")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n Остановлено пользователем")
