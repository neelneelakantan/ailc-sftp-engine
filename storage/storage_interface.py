from abc import ABC, abstractmethod

class BaseStorage(ABC):
    @abstractmethod
    def save(self, file_name: str, data: bytes) -> bool:
        """Saves data to the destination."""
        pass

    @abstractmethod
    def exists(self, file_name: str) -> bool:
        """Checks if a file exists."""
        pass

    @abstractmethod
    def get_hash(self, file_name: str) -> str:
        """Returns the SHA-256 hash of the stored file."""
        pass