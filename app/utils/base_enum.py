from enum import Enum


class StrEnum(str, Enum):
    """Parent Custom Enum Str

    В стандартном енуме сравнивается конечное значение, после =
    Но нам надо, чтобы код работал только с английскими значениями:
    сравнивал, записывал в БД и отдавал на фронт.
    А фронт брал английское значение и подставлял для него русское

    Usage:

    class SomeEngRusEnum(StrEnum):
        draft = "draft", "черновик"

    c = SomeEngRusEnum.choices
    [("draft", "черновик")]

    print(SomeEngRusEnum.draft.phrase == "Черновик")  # True
    print(SomeEngRusEnum.draft.name == "draft")  # True
    print(SomeEngRusEnum.draft == "draft")  # True
    """

    phrase: str

    def __new__(cls, value: str, phrase: str = None):
        obj = str.__new__(cls, value)

        obj._value_ = value
        obj.phrase = phrase

        return obj

    def __str__(self) -> str:
        return self._value_

    @classmethod
    @property
    def choices(cls):
        return [(status.name, status.phrase) for status in cls]
