import json
from dataclasses import asdict, dataclass
from datetime import datetime

from bson.objectid import ObjectId


@dataclass
class BaseEntity:
    _id: ObjectId
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dict(cls, data):
        """Convert data from a dictionary"""
        return cls(**data)

    def to_dict(self):
        """Convert data into dictionary"""
        return asdict(self)

    @property
    def id(self):
        return str(self._id)

    def to_json(self):
        def default_serializer(obj):
            if isinstance(obj, ObjectId):
                return str(obj)
            elif isinstance(obj, datetime):
                return obj.isoformat()
            return str(obj)

        return json.dumps(self.to_dict(), default=default_serializer, indent=4)
