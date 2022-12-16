import numpy as np


class Source:
    def __init__(self, source_shape: tuple):
        self._source_shape: tuple = source_shape

    def get_data(self) -> np.ndarray:
        return np.random.randint(
            256,
            size=self._source_shape,
            dtype=np.uint8,
        )
