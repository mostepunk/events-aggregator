import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio

from tests.fakers.fake_events_crud import FakeEventCRUD

from app.adapters.db.utils.expire import calculate_expires_at_by_severity
from app.adapters.schemas.events import EventCreateSchema
from app.dependencies.containers import Container
from app.services.events_service import EventService
from app.utils.data_generator import EventDataGenerator, random_event_generator
from app.utils.fake_client import fake


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


@pytest.fixture
def mock_event_crud():
    mock = AsyncMock()
    mock.convert_id_to_ObjectId = Mock(side_effect=lambda x: x)
    return mock


@pytest.fixture(scope="function")
def event_service_mocked(mock_event_crud):
    return EventService(mock_event_crud)


@pytest.fixture(scope="function")
def fake_event_crud(mock_event_crud):
    """В целом подход неплохой, но надо дублировать много кода,
    чтобы имитировать работу mongo
    """
    return FakeEventCRUD("events")


@pytest.fixture(scope="function")
def event_service_fake(fake_event_crud):
    """Сомнительно, но окэй."""
    return EventService(fake_event_crud)


@pytest.fixture()
def event_generator():
    return EventDataGenerator(seed=42)


@pytest.fixture()
def event_data():
    event = next(random_event_generator(1))
    event["created_at"] = datetime.now().isoformat()
    event["updated_at"] = datetime.now().isoformat()
    event["expired_at"] = calculate_expires_at_by_severity(event.get("severity"))
    event["_id"] = fake.mongo_id()
    return event


@pytest.fixture()
def event_schema(event_data):
    return EventCreateSchema(**event_data)
