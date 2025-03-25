"""
Класс, отвечающий за вывод ошибок ассемблирования. Содержит информацию
о месте, в котором был найден и построен `tracked` класс
"""

from dataclasses import dataclass
from typing import Any
from functools import wraps

# @dataclasses(frozen=True)
# class TrackedError(Exception):
    


@dataclass
class TrackedInfo:
    """
    Информация о том, в какой строке и в каком месте
    было инициировано создание объекта, а также
    опциональная ссылка на сам объект
    """
    lineno: int
    index: int
    obj: Any = None

@dataclass
class TrackedError(Exception):
    failed_on: Any
    prev_exception: Exception | None = None


class ErrorWatcher:
    """
    Синглтон класс, хранящий отладочную информацию о расположении
    того ассемблерного текста, который породил какой-то объект
    """
    instance: "ErrorWatcher"

    def __new__(cls) -> "ErrorWatcher":
        if not hasattr(cls, "instance"):
            cls.instance = super(ErrorWatcher, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        if not hasattr(self, "tracked_table"):
            self.tracked_table: dict[int, TrackedInfo] = {}

    def report_error(self, error):
        pass
    
    def get_id(self) -> int:
        id_ = 0
        while id_ in self.tracked_table:
            id_ += 1
        return id_

    def add_tracked(self, id_: int, lineno: int, index_: int, obj: Any = None) -> None:
        if id_ in self.tracked_table:
            raise IndexError("You try to overwrite existing tracked object")
        self.tracked_table[id_] = TrackedInfo(lineno, index_, obj)

    def get_info_by_object(self, obj: Any):
        if hasattr(obj, "id_"):
            return self.tracked_table[obj.id_]

    def get_info_by_id(self, id_: int):
        return self.tracked_table[id_]

    def add_info(self, id_: int, info: TrackedInfo):
        self.tracked_table[id_] = info

    def update_info(
            self,
            id_: int,
            lineno: int | None = None,
            index: int | None = None,
            obj: Any = None
            ) -> None:
        if not id_ in self.tracked_table:
            return
        info = self.tracked_table[id_]
        if lineno:
            info.lineno = lineno
        if index:
            info.index = index
        if obj:
            info.obj = obj

    def drop_tracked_table(self) -> None:
        self.tracked_table = {}

    def drop_by_id(self, id_: int) -> None:
        if id_ in self.tracked_table:
            del self.tracked_table[id_]

    def drop_obj(self, obj: Any):
        if hasattr(obj, "_id"):
            self.drop_by_id(obj._id)

def tracked(cls: type):
    """
    Декоратор для классов, который модифицирует метод __new__ таким образом
    чтобы при вызове в ErrorWatcher добавлялся уникальный id. Учтите, что этот
    декоратор следует в общем случае вешать на класс последним в иерархии
    """
    old_init = cls.__init__
    def init(self: Any, *args, **kwargs) -> None:
        old_init(self, *args, **kwargs)
        id_: int = ErrorWatcher().get_id()
        if hasattr(self, "_id"):
            raise AttributeError("Looks like class "
                                 f"\"{self.__class__.__name__}\" "
                                 "already defined field \"_id\" needed by "
                                 "`tracked` decorator")
        setattr(self, "_id", id_)
        ErrorWatcher().add_tracked(id_, -1, -1, self)
    cls.__init__ = init
    return cls

