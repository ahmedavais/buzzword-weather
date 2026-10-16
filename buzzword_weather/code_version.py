import hashlib
from pathlib import Path


def code_version(folder: Path) -> str:
    digest = hashlib.sha256()
    for file in sorted(folder.glob("*.py")):
        digest.update(file.name.encode())
        digest.update(file.read_bytes())
    return digest.hexdigest()
