from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from zipfile import BadZipFile, ZipFile, is_zipfile

from hzltfw.core.models import EvidenceFile, EvidenceItem
from hzltfw.core.plugin import ArtifactCreate, PluginContext
from hzltfw.plugins.keyword_search import regex_rules

SUSPICIOUS_NAME_KEYWORDS = (
    "course",
    "leak",
    "password",
    "secret",
    "资料",
    "课程",
    "密码",
    "泄露",
)


class ArchiveIndexPlugin:
    name = "archive_index"
    version = "0.1.0"
    description = "Index ZIP archive entries without extracting them."
    plugin_type = "evidence"
    artifact_types = ["archive.index", "archive.entry"]

    def analyze_evidence(
        self,
        context: PluginContext,
        evidence: EvidenceItem,
        files: list[EvidenceFile],
    ) -> list[ArtifactCreate]:
        del evidence

        artifacts: list[ArtifactCreate] = []
        rules = regex_rules(context.config)
        for file in files:
            if not _supports_zip(file):
                continue
            entries = _zip_entries(Path(file.absolute_path or ""))
            if entries is None:
                continue

            suspicious_entries = [
                entry for entry in entries if _suspicious_reasons(entry["path"], rules)
            ]
            artifacts.append(_archive_index_artifact(file, entries, suspicious_entries))
            artifacts.extend(
                _archive_entry_artifact(file, entry, rules)
                for entry in suspicious_entries
            )

        return artifacts


def _supports_zip(file: EvidenceFile) -> bool:
    return (
        not file.is_virtual
        and file.absolute_path is not None
        and file.extension.lower() == ".zip"
        and is_zipfile(file.absolute_path)
    )


def _zip_entries(path: Path) -> list[dict[str, Any]] | None:
    try:
        with ZipFile(path) as archive:
            return [_entry_data(info) for info in archive.infolist()]
    except (BadZipFile, OSError):
        return None


def _entry_data(info) -> dict[str, Any]:  # noqa: ANN001
    modified_at = _zip_datetime(info.date_time)
    return {
        "path": info.filename,
        "is_dir": info.is_dir(),
        "uncompressed_size": info.file_size,
        "compressed_size": info.compress_size,
        "modified_at": modified_at.isoformat() if modified_at else None,
    }


def _zip_datetime(value: tuple[int, int, int, int, int, int]) -> datetime | None:
    try:
        return datetime(*value, tzinfo=UTC)
    except ValueError:
        return None


def _archive_index_artifact(
    file: EvidenceFile,
    entries: list[dict[str, Any]],
    suspicious_entries: list[dict[str, Any]],
) -> ArtifactCreate:
    file_entries = [entry for entry in entries if not entry["is_dir"]]
    return ArtifactCreate(
        artifact_type="archive.index",
        title=f"ZIP archive indexed: {file.relative_path}",
        summary=(
            f"Indexed {len(entries)} entries in {file.relative_path}; "
            f"{len(suspicious_entries)} suspicious entry names found."
        ),
        source_path=file.relative_path,
        timestamp=file.mtime,
        severity="medium" if suspicious_entries else "info",
        is_key=bool(suspicious_entries),
        tags=["archive", "zip"],
        data={
            "archive_type": "zip",
            "entry_count": len(entries),
            "file_count": len(file_entries),
            "directory_count": len(entries) - len(file_entries),
            "suspicious_entry_count": len(suspicious_entries),
            "entries": entries,
        },
    )


def _archive_entry_artifact(
    file: EvidenceFile,
    entry: dict[str, Any],
    rules,
) -> ArtifactCreate:  # noqa: ANN001
    reasons = _suspicious_reasons(entry["path"], rules)
    return ArtifactCreate(
        artifact_type="archive.entry",
        title=f"Suspicious archive entry: {entry['path']}",
        summary=(
            f"{entry['path']} in {file.relative_path} "
            f"matched {', '.join(reasons)}."
        ),
        source_path=f"{file.relative_path}!/{entry['path']}",
        timestamp=file.mtime,
        severity="medium",
        is_key=True,
        tags=["archive", "zip", "suspicious_name", *reasons],
        data={
            "archive_path": file.relative_path,
            "entry": entry,
            "reasons": reasons,
        },
    )


def _suspicious_reasons(path: str, rules) -> list[str]:  # noqa: ANN001
    lowered = path.lower()
    reasons = [
        f"name:{keyword}"
        for keyword in SUSPICIOUS_NAME_KEYWORDS
        if keyword.lower() in lowered
    ]
    reasons.extend(
        f"regex:{rule.name}" for rule in rules if rule.pattern.search(path)
    )
    return reasons
