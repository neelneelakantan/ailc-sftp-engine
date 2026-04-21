import hashlib


def generate_sha256(data: bytes) -> str:
    """Generates a SHA-256 hash for a block of bytes."""
    return hashlib.sha256(data).hexdigest()

def hash_file(filepath: str, block_size: int = 65536) -> str:
    """Hashes an existing file on disk incrementally."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            sha256.update(block)
    return sha256.hexdigest()