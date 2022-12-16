from scipy.ndimage import zoom, median_filter

from queues import Image


def transform(img: Image) -> Image:
    resized = zoom(img, zoom=(0.5, 0.5, 1))
    filtered = median_filter(resized, size=(5, 5, 1))
    return filtered
