from typing import Tuple

from scipy.ndimage import zoom, median_filter

from queues import Image


def make_transform(zoom_factor: float, kernel_size: Tuple[int, int]):
    def transform(img: Image) -> Image:
        resized = zoom(img, zoom=(zoom_factor, zoom_factor, 1))
        filtered = median_filter(resized, size=(*kernel_size, 1))
        return filtered

    return transform
