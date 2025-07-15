import asyncio
from uuid import uuid4

import pytest
import pytest_asyncio

from tests.fakers.fake_events_crud import FakeEventCRUD

from app.adapters.schemas.events import EventCreateSchema
from app.dependencies.containers import Container
from app.services.events_service import EventService


@pytest_asyncio.fixture(autouse=True)
async def container_teardown():
    try:
        yield
    finally:
        await Container.tear_down()


@pytest.fixture(autouse=True)
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def event_service():
    return EventService(FakeEventCRUD("events"))


@pytest.fixture()
def event_data():
    data = {
        "event_type": "notification",
        "event_data": {"username": "Pupkin", "redirect_url": "https://example.com"},
        "user_id": str(uuid4()),
        "source": "email",
        "level": "info",
        "tags": ["tag1", "tag2"],
    }
    return EventCreateSchema(**data)
