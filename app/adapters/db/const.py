from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MongoCollections:
    events = "events"
    rules = "rules"
    metrics = "metrics"
    users = "users"
    index_metrics = "index_metrics"
