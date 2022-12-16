from dataclasses import dataclass
from itertools import islice, count
from pathlib import Path
from queue import Queue
from time import sleep
from typing import Optional, Callable

import numpy as np
from matplotlib.image import imsave

from source import Source

Image = np.ndarray


@dataclass(frozen=True)
class ImageTask:
    id: int
    type: str
    image: Image


Task = Optional[ImageTask]
Transform = Callable[[Image], Image]


def ingest(source: Source, target: Queue[Task], *,
           limit: Optional[int] = None, interval_ms: int) -> None:
    counter = islice(count(start=1), limit)

    for task_id in counter:
        item = ImageTask(task_id, 'input', source.get_data())
        target.put(item)
        sleep(interval_ms / 1000)

    # put a sentinel to signal that no other items will need to be processed
    target.put(None)


def process(source: Queue[Task], transform: Transform, target: Queue[Task]) -> None:
    while task := source.get():
        match task:
            case ImageTask(task_id, _, image):
                target.put(ImageTask(task_id, 'output', transform(image)))
                source.task_done()

    # put a sentinel to signal that no other items will need to be processed
    target.put(None)


def save(source: Queue[Task], directory: Path) -> None:
    while task := source.get():
        match task:
            case ImageTask(task_id, task_type, image):
                file = directory / f'{task_type}_{task_id}.png'
                imsave(file, image)
                source.task_done()
