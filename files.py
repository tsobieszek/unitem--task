from pathlib import Path
from typing import Protocol, TypeVar

T_contra = TypeVar('T_contra', contravariant=True)


class FileSaver(Protocol[T_contra]):
    def save(self, path: Path, content: T_contra) -> None: ...

    @staticmethod
    def extension() -> str: ...
