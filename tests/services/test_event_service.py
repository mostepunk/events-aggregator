from app.entities.event import Event


class TestEventService:
    """TestEventService."""

    async def test_create_events(self, event_service, event_data):
        """Успешное создание событий."""
        events = [event_data.dict() for _ in range(10)]
        res = await event_service.create_events(events)

        assert len(res) == 10, "Должно быть создано 10 событий"
        assert all(
            isinstance(event, Event) for event in res
        ), "Содержимое должно быть экземпляром Event"
        assert event_service.repo.called_count == 2, "Должно быть вызвано 2 запроса"

    async def test_get_recent_events(self, event_service):
        """Успешное получение последних событий."""
        res = await event_service.get_recent_events()
        assert isinstance(res, list), "Должно быть список"
        assert all(
            isinstance(event, Event) for event in res
        ), "Содержимое должно быть экземпляром Event"
        assert event_service.repo.called_count == 1, "Должен быть вызван 1 запрос"

    async def test_get_recent_events_empty(self, event_service):
        """Пустой список событий."""
        event_service.repo.data = []
        res = await event_service.get_recent_events()
        assert res == [], "Должен быть пустой список"
