from app.entities.event import Event


class TestEventService:
    """TestEventService.

    Тестирование бизнес-логики сервисного слоя.
    """

    async def test_create_events_calls_correct_methods(
        self, event_service_mocked, mock_event_crud, event_data
    ):
        events = [event_data for _ in range(10)]
        mock_ids = ["id1", "id2"]
        mock_events = [Event(**event) for event in events]

        mock_event_crud.bulk_create.return_value = mock_ids
        mock_event_crud.get_all.return_value = mock_events

        result = await event_service_mocked.create_events(events)

        # методы должны быть вызваны
        mock_event_crud.bulk_create.assert_called_once_with(events)
        mock_event_crud.get_all.assert_called_once_with({"_id": {"$in": mock_ids}})

        for res in result:
            # сервисный слой должен возвращать словари
            assert isinstance(res, dict)
            assert isinstance(res.get("_id"), str)

    async def test_get_recent_events_calls_correct_methods(
        self, mock_event_crud, event_data, event_service_mocked
    ):
        mock_events = [Event(**event_data) for _ in range(10)]
        mock_event_crud.get_recent_events.return_value = mock_events

        await event_service_mocked.get_recent_events()

        mock_event_crud.get_recent_events.assert_called_once()
