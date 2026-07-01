from pathlib import Path

from sqlalchemy import delete
from sqlmodel import Session

from hzltfw.core.exceptions import EvidenceSourceNotFoundError
from hzltfw.core.models import EvidenceFile, EvidenceItem
from hzltfw.utils.timestamps import from_timestamp


def scan_evidence(session: Session, evidence: EvidenceItem) -> list[EvidenceFile]:
    source = Path(evidence.source_path).expanduser().resolve()
    if not source.exists():
        raise EvidenceSourceNotFoundError

    session.exec(delete(EvidenceFile).where(EvidenceFile.evidence_id == evidence.id))

    files = list(_iter_source_files(source))
    indexed_files = [_build_evidence_file(evidence, source, path) for path in files]
    evidence.size_bytes = sum(file.size_bytes for file in indexed_files)

    session.add(evidence)
    session.add_all(indexed_files)
    session.commit()

    for file in indexed_files:
        session.refresh(file)
    session.refresh(evidence)
    return indexed_files


def _iter_source_files(source: Path) -> list[Path]:
    if source.is_file():
        return [source]
    return sorted(path for path in source.rglob("*") if path.is_file())


def _build_evidence_file(
    evidence: EvidenceItem,
    source: Path,
    path: Path,
) -> EvidenceFile:
    stat = path.stat()
    relative_path = (
        path.name if source.is_file() else path.relative_to(source).as_posix()
    )
    return EvidenceFile(
        evidence_id=evidence.id or 0,
        relative_path=relative_path,
        absolute_path=str(path),
        virtual_path=f"{evidence.name}/{relative_path}",
        size_bytes=stat.st_size,
        mtime=from_timestamp(stat.st_mtime),
        ctime=from_timestamp(stat.st_ctime),
        extension=path.suffix.lower(),
        is_virtual=False,
    )
