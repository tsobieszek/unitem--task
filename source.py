from typing import Protocol, TypeVar

import numpy as np


T_co = TypeVar('T_co', covariant=True)

class DataSource(Protocol[T_co]):
    def get_data(self) -> T_co: ...


class Source:
    def __init__(self, source_shape: tuple):
        self._source_shape: tuple = source_shape

    def get_data(self) -> np.ndarray:
        return np.random.randint(
            256,
            size=self._source_shape,
            dtype=np.uint8,
        )
