from itertools import islice, count
from pathlib import Path
from queue import Queue
from time import sleep
from typing import Optional, Callable, TypeVar

from files import FileSaver
from source import DataSource
from tasks import RealTask, End, Task

T = TypeVar('T')
TaskQueue = Queue[Task[T]]
Transform = Callable[[T], T]


def ingest(source: DataSource[T], target: TaskQueue[T], *,
           limit: Optional[int] = None, interval_ms: int = 0) -> None:
    counter = islice(count(start=1), limit)

    for task_id in counter:
        item = RealTask(task_id, 'input', source.get_data())
        target.put(item)
        sleep(interval_ms / 1000)

    # put a sentinel to signal that no other items will need to be processed
    target.put(End)


def process(source: TaskQueue[T], transform: Transform[T], target: TaskQueue[T]) -> None:
    while task := source.get():
        match task:
            case RealTask(task_id, _, content):
                target.put(RealTask(task_id, 'output', transform(content)))
                source.task_done()

    # put a sentinel to signal that no other items will need to be processed
    target.put(End)


def save(source: TaskQueue[T], directory: Path, saver: FileSaver[T]) -> None:
    while task := source.get():
        match task:
            case RealTask(task_id, task_type, content):
                file = directory / f'{task_type}_{task_id}.{saver.extension()}'
                saver.save(file, content)
                source.task_done()
