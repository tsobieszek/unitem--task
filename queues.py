import logging
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
    """
    Periodically ingest data from a data source (`source`), enclose each of them in a `RealTask` container
    and put such containers in a queue (`target`).

    If `limit` is not None then stop after having processed `limit` elements and put the `End`
    sentinel at the end of the queue.

    Each task is provided with a sequential `id` (starting from 1) and the `type` field is set to 'input'.

    :param source: Input DataSource.
    :param target: Output Queue of Tasks.
    :param limit: The number of data items to ingest into the queue. Defaults to `None`.
    :param interval_ms: The interval to sleep between retrieving data. Defaults to 0.
    """
    counter = islice(count(start=1), limit)

    for task_id in counter:
        logging.info(f'Ingesting task {task_id} from source')
        item = RealTask(task_id, 'input', source.get_data())
        target.put(item)
        sleep(interval_ms / 1000)

    # put a sentinel to signal that no other items will need to be processed
    target.put(End)


def process(source: TaskQueue[T], transform: Transform[T], target: TaskQueue[T]) -> None:
    """
    Retrieve tasks from `source` queue, transform the content of each task using `transform`,
    enclose it in a `RealTask` container and push it to the `target` queue.

    Processing stops if and when the `End` sentinel is retrieved from the `source` in which case the `End`
    sentinel is put into the target.

    The `id` of the output task is set to the id of the input. The `type` is set to 'output'.

    :param source: Input Queue of Tasks.
    :param transform: The transform to apply to the content of each task.
    :param target: Output Queue of Tasks.
    """
    while task := source.get():
        match task:
            case RealTask(task_id, _, content):
                logging.info(f'processing task {task_id}')
                target.put(RealTask(task_id, 'output', transform(content)))
                source.task_done()

    # put a sentinel to signal that no other items will need to be processed
    target.put(End)


def save(source: TaskQueue[T], directory: Path, saver: FileSaver[T]) -> None:
    """
    Retrieve tasks from `source` queue and saves their content as a file in a `directory`.

    The name of the file is `type_id.ext` where `type` and `id` are metadata fields of
    a given task (`RealTask`). The extension is provided by `saver`.

    Processing stops if and when the `End` sentinel is retrieved from the `source`.

    :param source: Input Queue of Tasks.
    :param directory: Directory in which the files are saved.
    :param saver: `FileSaver`
    """
    while task := source.get():
        match task:
            case RealTask(task_id, task_type, content):
                file = directory / f'{task_type}_{task_id}.{saver.extension()}'
                logging.info(f'Saving processed task {task_id} to {file}')
                saver.save(file, content)
                source.task_done()
