
import os

from storage.storage_interface import BaseStorage
from core.observability.logger import logger
from core.deterministic_layer.hasher import hash_file


class LocalStorage(BaseStorage):
    def __init__(self, base_path: str):
        self.base_path = base_path
        if not os.path.exists(base_path):
            os.makedirs(base_path)

    def save(self, file_name: str, data: bytes) -> bool:
        try:
            full_path = os.path.join(self.base_path, file_name)
            with open(full_path, "wb") as f:
                f.write(data)
            logger.info(f"File saved locally: {file_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to save local file: {str(e)}")
            return False

    def exists(self, file_name: str) -> bool:
        return os.path.exists(os.path.join(self.base_path, file_name))
    
    def get_hash(self, file_name: str) -> str:
        full_path = os.path.join(self.base_path, file_name)
        if self.exists(file_name):
            return hash_file(full_path)
        return ""
    