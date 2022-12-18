from dataclasses import dataclass
from typing import TypeVar, Generic

from singleton_decorator import singleton

T_co = TypeVar('T_co', covariant=True)


@dataclass(frozen=True)
class RealTask(Generic[T_co]):
    id: int
    type: str
    content: T_co


@singleton
class EndType:
    """Sentinel used to signal the end of processing"""

    def __bool__(self):
        return False


End = EndType()
Task = RealTask[T_co] | EndType
