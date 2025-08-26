from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MongoCollections:
    events = "events"
    rules = "rules"
    users = "users"
    index_metrics = "index_metrics"
    profiler_stat = "profiler_stat"
