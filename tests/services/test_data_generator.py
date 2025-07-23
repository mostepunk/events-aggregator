from app.utils.data_generator import (
    generate_critical_events,
    generate_info_events,
    random_event_data,
    stream_events,
)


class TestDataGenerator:

    def test_stream_events(self):
        events = []
        end = 0
        for event in stream_events():
            events.append(event)
            end += 1
            if end == 2:
                break

        assert len(events) == 2, f"Expected 2 events, got {len(events)}"
        for event in events:
            assert isinstance(event, dict), f"Expected dict, got {type(event)}"

    def test_generate_critical_events(self):
        events = list(generate_critical_events(2))

        assert len(events) == 2, f"Expected 2 events, got {len(events)}"
        for event in events:
            assert isinstance(event, dict), f"Expected dict, got {type(event)}"
            assert event["severity"] in (
                7,
                8,
                9,
                10,
            ), f"Expected severity in (7, 8, 9, 10), got {event['severity']}"

    def test_generate_info_events(self):
        events = list(generate_info_events(2))

        assert len(events) == 2, f"Expected 2 events, got {len(events)}"
        for event in events:
            assert isinstance(event, dict), f"Expected dict, got {type(event)}"
            assert event["severity"] in (
                1,
                2,
                3,
                4,
                5,
                6,
            ), f"Expected severity in (1, 2, 3, 4, 5, 6), got {event['severity']}"

    def test_generate_random_event_data(self):
        event = list(random_event_data(2))

        assert len(event) == 2, f"Expected 2 events, got {len(event)}"
        for event in event:
            assert isinstance(event, dict), f"Expected dict, got {type(event)}"
