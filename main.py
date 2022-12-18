from pathlib import Path
from queue import Queue
from threading import Thread
from typing import NamedTuple

import images
import queues
from images import Image, PngImageSaver
from queues import TaskQueue
from source import Source, DataSource

ImageDataSource = DataSource[Image]
ImageTaskQueue = TaskQueue[Image]


def main() -> None:
    source = Source(ImageShape(width=1024, height=768, channels=3))  # type: ImageDataSource

    queue_a = Queue(maxsize=16)  # type: ImageTaskQueue
    queue_b = Queue(maxsize=16)  # type: ImageTaskQueue

    save_dir = Path('processed')
    save_dir.mkdir(parents=True, exist_ok=True)

    transform1 = images.resize(zoom_factor=0.5)
    transform2 = images.median_filter(kernel_size=(5, 5))
    transform = lambda img: transform2(transform1(img))

    ingesting = Thread(target=queues.ingest,
                       args=(source, queue_a),
                       kwargs={'limit': 100, 'interval_ms': 50})
    transforming = Thread(target=queues.process,
                          args=(queue_a, transform, queue_b))

    ingesting.start()
    transforming.start()
    queues.save(queue_b, save_dir, PngImageSaver())


class ImageShape(NamedTuple):
    height: int
    width: int
    channels: int


if __name__ == '__main__':
    main()
