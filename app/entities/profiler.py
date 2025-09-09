from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Optional

from app import getLogger

logging = getLogger(__name__)


def camelcase_to_snake(name: str) -> str:
    for char in name:
        if char.isupper():
            name = name.replace(char, "_" + char.lower())
    return name


@dataclass
class Profiler:
    was: int
    slowms: int
    sample_rate: float
    ok: float
    stop_time: Optional[datetime] = None

    def to_dict(self, verbose: bool = False):
        """Конвертировать данные в словарь."""
        data = asdict(self)
        if not verbose:
            return data

        verbose_data = {}
        for key, value in data.items():
            verbose_data["level"] = self.was
            verbose_data["level_verbose"] = self.level_verbose
            verbose_data["slowms"] = self.slowms
            verbose_data["till"] = self.stop_time
        return verbose_data

    @classmethod
    def from_dict(cls, data: dict):
        """Конвертировать данные из словаря в объект."""
        to_remove = {}
        for key, value in data.items():
            new_key = camelcase_to_snake(key)
            to_remove[key] = new_key

        for old_key, new_key in to_remove.items():
            data[new_key] = data.pop(old_key)

        return cls(**data)

    @property
    def is_enabled(self) -> bool:
        """Включен ли профайлер.

        0 - Profiler is off and does not collect any data (default).
        1 - Profiler collects data for operations that exceed the slowms threshold.
        2 - Profiler collects data for all operations.
        """
        if self.was == 0:
            return False
        return True

    @property
    def is_disabled(self) -> bool:
        """Профайлер полностью отключен"""
        return self.was == 0

    @property
    def level_verbose(self) -> str:
        """Человекочитаемое описание уровня"""
        descriptions = {
            0: "Disabled - no data collection",
            1: f"Slow operations only (>{self.slowms}ms)",
            2: "All operations",
        }
        return descriptions.get(self.was, "Unknown level")

    @property
    def slowms_threshold_seconds(self) -> float:
        """Порог медленных операций в секундах"""
        return self.slowms / 1000.0
