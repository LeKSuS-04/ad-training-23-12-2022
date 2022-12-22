import subprocess
from pathlib import Path

from abc import ABC, abstractmethod


class StorageException(Exception):
    pass


class AbstractStorage(ABC):
    @abstractmethod
    def store(self, collection: str, key: str, value: str) -> None:
        ...

    @abstractmethod
    def remove(self, collection: str, key: str) -> None:
        ...

    @abstractmethod
    def get(self, collection: str, key: str) -> str:
        ...

    @abstractmethod
    def list(self, collection: str) -> list[str]:
        ...

    def size(self, collection: str) -> int:
        return len(self.list(collection))


class FileSystemStorage(AbstractStorage):
    def __init__(self, base_path: Path):
        self.base = base_path.resolve()

    def ensure_collection_exists(self, collection: str) -> None:
        (self.base / collection).mkdir(parents=True, exist_ok=True)

    def store(self, collection: str, key: str, value: str) -> None:
        self.ensure_collection_exists(collection)
        with open(str(self.base / collection / key), 'w') as f:
            f.write(value)

    def remove(self, collection: str, key: str) -> None:
        (self.base / collection / key).unlink()

    def get(self, collection: str, key: str) -> str:
        if key == '' or '..' in key or '%' in key:
            raise StorageException()

        try:
            proc = subprocess.run(
                ['curl', f'file://{str(self.base / collection / key)}'],
                capture_output=True,
                timeout=1,
            )
        except subprocess.TimeoutExpired:
            raise StorageException()

        if proc.returncode != 0:
            raise StorageException()

        return proc.stdout.decode()

    def list(self, collection: str) -> list[str]:
        self.ensure_collection_exists(collection)
        return [str(path.name) for path in (self.base / collection).iterdir()]
