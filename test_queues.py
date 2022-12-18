from itertools import count
from pathlib import Path
from queue import Queue

import pytest

import queues
from tasks import End, RealTask


def test_ingest(source, target_queue):
    # when
    queues.ingest(source, target_queue, limit=2, interval_ms=0)
    t1 = target_queue.get()
    t2 = target_queue.get()
    t3 = target_queue.get()
    # then
    assert t1 == RealTask(1, 'input', 0)
    assert t2 == RealTask(2, 'input', 1)
    assert t3 == End
    assert target_queue.empty()


def test_process(source_queue, transform, target_queue):
    # when
    queues.process(source_queue, transform, target_queue)
    t1 = target_queue.get()
    t2 = target_queue.get()
    t3 = target_queue.get()
    # then
    assert t1 == RealTask(1, 'output', 'aa')
    assert t2 == RealTask(2, 'output', 'bb')
    assert t3 == End
    assert target_queue.empty()


def test_save(source_queue, tmp_path, file_saver):
    # when
    queues.save(source_queue, tmp_path, file_saver)
    paths = file_saver.paths
    contents = file_saver.elems
    # then
    assert len(paths) == len(contents) == 2
    assert paths[0] == tmp_path / 'test_1.txt'
    assert paths[1] == tmp_path / 'test_2.txt'
    assert contents == ['a', 'b']


@pytest.fixture()
def source():
    class Source():
        def __init__(self):
            self.it = count(start=0)

        def get_data(self) -> int:
            return next(self.it)

    return Source()


@pytest.fixture()
def source_queue():
    q = Queue()
    q.put(RealTask(1, 'test', 'a'))
    q.put(RealTask(2, 'test', 'b'))
    q.put(End)
    return q


@pytest.fixture()
def transform():
    return lambda x: 2 * x


@pytest.fixture()
def target_queue():
    return Queue()


@pytest.fixture()
def file_saver():
    class MockFileSaver:
        def __init__(self):
            self.paths = []
            self.elems = []

        def save(self, path: Path, content: str) -> None:
            self.paths.append(path)
            self.elems.append(content)

        @staticmethod
        def extension() -> str:
            return 'txt'

    return MockFileSaver()
