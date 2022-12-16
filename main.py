from pathlib import Path
from typing import NamedTuple

import images
from source import Source
import queues
from threading import Thread
from queue import Queue


def main():
    source = Source(ImageShape(width=1024, height=768, channels=3))

    queue_a = Queue(maxsize=16)
    queue_b = Queue(maxsize=16)

    save_dir = Path('processed')
    save_dir.mkdir(parents=True, exist_ok=True)

    transform = images.transform

    ingesting = Thread(target=queues.ingest, args=(source, queue_a), kwargs={'limit': 100, 'interval_ms': 50})
    transforming = Thread(target=queues.process, args=(queue_a, transform, queue_b))

    ingesting.start()
    transforming.start()
    queues.save(queue_b, save_dir)


class ImageShape(NamedTuple):
    height: int
    width: int
    channels: int


if __name__ == '__main__':
    main()
