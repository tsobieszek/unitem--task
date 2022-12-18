from pathlib import Path
from typing import Tuple

import numpy as np
from matplotlib import image
from scipy import ndimage

from files import FileSaver
from queues import Transform

Image = np.ndarray


def resize(zoom_factor: float, ) -> Transform:
    def transform(img: Image) -> Image:
        return ndimage.zoom(img, zoom=(zoom_factor, zoom_factor, 1))

    return transform


def median_filter(kernel_size: Tuple[int, int]) -> Transform:
    def transform(img: Image) -> Image:
        return ndimage.median_filter(img, size=(*kernel_size, 1))

    return transform


class PngImageSaver(FileSaver[Image]):
    def save(self, path: Path, content: Image) -> None:
        image.imsave(path, content)

    @staticmethod
    def extension():
        return 'png'
