from hashlib import md5, sha1, sha256
from pathlib import Path


def hash_file(path: str | Path, chunk_size: int = 1024 * 1024) -> dict[str, str]:
    md5_hash = md5(usedforsecurity=False)
    sha1_hash = sha1(usedforsecurity=False)
    sha256_hash = sha256()

    with Path(path).open("rb") as file:
        for chunk in iter(lambda: file.read(chunk_size), b""):
            md5_hash.update(chunk)
            sha1_hash.update(chunk)
            sha256_hash.update(chunk)

    return {
        "md5": md5_hash.hexdigest(),
        "sha1": sha1_hash.hexdigest(),
        "sha256": sha256_hash.hexdigest(),
    }
