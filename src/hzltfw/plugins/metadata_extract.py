from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from docx import Document
from PIL import ExifTags, Image
from pypdf import PdfReader

from hzltfw.core.models import EvidenceFile, EvidenceItem
from hzltfw.core.plugin import ArtifactCreate, PluginContext

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}
PDF_EXTENSIONS = {".pdf"}
DOCX_EXTENSIONS = {".docx"}
MIN_PDF_YEAR_LENGTH = 4
MIN_PDF_TIMEZONE_LENGTH = 3
MIN_PDF_TIMEZONE_DIGITS = 2
PDF_DATE_LENGTH = 14


class MetadataExtractPlugin:
    name = "metadata_extract"
    version = "0.1.0"
    description = "Extract image, PDF, and DOCX metadata."
    plugin_type = "file"
    artifact_types = ["metadata.image", "metadata.pdf", "metadata.office"]

    def supports(self, file: EvidenceFile) -> bool:
        return (
            not file.is_virtual
            and file.absolute_path is not None
            and file.extension.lower()
            in IMAGE_EXTENSIONS | PDF_EXTENSIONS | DOCX_EXTENSIONS
        )

    def analyze_file(
        self,
        context: PluginContext,
        evidence: EvidenceItem,
        file: EvidenceFile,
    ) -> list[ArtifactCreate]:
        del context, evidence

        path = Path(file.absolute_path or "")
        extension = file.extension.lower()
        if extension in IMAGE_EXTENSIONS:
            artifact = _image_metadata(file, path)
        elif extension in PDF_EXTENSIONS:
            artifact = _pdf_metadata(file, path)
        elif extension in DOCX_EXTENSIONS:
            artifact = _docx_metadata(file, path)
        else:
            artifact = None
        return [artifact] if artifact else []


def _image_metadata(file: EvidenceFile, path: Path) -> ArtifactCreate | None:
    try:
        with Image.open(path) as image:
            exif = _image_exif(image)
            data = {
                "format": image.format,
                "mode": image.mode,
                "width": image.width,
                "height": image.height,
                "exif": exif,
            }
    except OSError:
        return None

    camera = " ".join(
        value
        for value in (exif.get("Make"), exif.get("Model"))
        if isinstance(value, str) and value
    )
    summary = f"{file.relative_path} image metadata extracted."
    if camera:
        summary = f"{summary} Camera: {camera}."
    return ArtifactCreate(
        artifact_type="metadata.image",
        title=f"Image metadata: {file.relative_path}",
        summary=summary,
        source_path=file.relative_path,
        timestamp=file.mtime,
        severity="info",
        tags=["metadata", "image"],
        data=data,
    )


def _image_exif(image: Image.Image) -> dict[str, Any]:
    exif: dict[str, Any] = {}
    for tag_id, value in image.getexif().items():
        tag = ExifTags.TAGS.get(tag_id, str(tag_id))
        exif[tag] = _json_value(value)
    return exif


def _pdf_metadata(file: EvidenceFile, path: Path) -> ArtifactCreate | None:
    try:
        reader = PdfReader(path)
    except Exception:  # noqa: BLE001
        return None

    raw_metadata = reader.metadata or {}
    metadata = {
        _clean_pdf_key(key): _json_value(value)
        for key, value in raw_metadata.items()
        if value not in (None, "")
    }
    created_at = _parse_pdf_datetime(metadata.get("CreationDate"))
    modified_at = _parse_pdf_datetime(metadata.get("ModDate"))
    title = metadata.get("Title") or file.relative_path
    author = metadata.get("Author")
    summary = f"{file.relative_path} PDF metadata extracted; {len(reader.pages)} pages."
    if author:
        summary = f"{summary} Author: {author}."
    return ArtifactCreate(
        artifact_type="metadata.pdf",
        title=f"PDF metadata: {title}",
        summary=summary,
        source_path=file.relative_path,
        timestamp=modified_at or created_at or file.mtime,
        severity="info",
        tags=["metadata", "pdf"],
        data={
            "page_count": len(reader.pages),
            "metadata": metadata,
            "created_at": created_at.isoformat() if created_at else None,
            "modified_at": modified_at.isoformat() if modified_at else None,
        },
    )


def _docx_metadata(file: EvidenceFile, path: Path) -> ArtifactCreate | None:
    try:
        document = Document(path)
    except Exception:  # noqa: BLE001
        return None

    properties = document.core_properties
    metadata = {
        "title": properties.title,
        "subject": properties.subject,
        "author": properties.author,
        "last_modified_by": properties.last_modified_by,
        "keywords": properties.keywords,
        "comments": properties.comments,
        "category": properties.category,
        "created": _iso_datetime(properties.created),
        "modified": _iso_datetime(properties.modified),
    }
    metadata = {
        key: value for key, value in metadata.items() if value not in (None, "")
    }
    created_at = _aware_datetime(properties.created)
    modified_at = _aware_datetime(properties.modified)
    title = metadata.get("title") or file.relative_path
    author = metadata.get("author")
    summary = f"{file.relative_path} DOCX core properties extracted."
    if author:
        summary = f"{summary} Author: {author}."
    return ArtifactCreate(
        artifact_type="metadata.office",
        title=f"Office metadata: {title}",
        summary=summary,
        source_path=file.relative_path,
        timestamp=modified_at or created_at or file.mtime,
        severity="info",
        tags=["metadata", "office", "docx"],
        data={"metadata": metadata},
    )


def _clean_pdf_key(key: str) -> str:
    return key.removeprefix("/")


def _parse_pdf_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    text = value.removeprefix("D:")
    if len(text) < MIN_PDF_YEAR_LENGTH:
        return None

    date_part = text[:PDF_DATE_LENGTH].ljust(PDF_DATE_LENGTH, "0")
    try:
        parsed = datetime.strptime(date_part, "%Y%m%d%H%M%S")  # noqa: DTZ007
    except ValueError:
        return None

    timezone_part = text[PDF_DATE_LENGTH:]
    if timezone_part in ("Z", "z"):
        return parsed.replace(tzinfo=UTC)
    if (
        timezone_part
        and timezone_part[0] in "+-"
        and len(timezone_part) >= MIN_PDF_TIMEZONE_LENGTH
    ):
        offset = _pdf_timezone_offset(timezone_part)
        if offset is not None:
            return parsed.replace(tzinfo=offset).astimezone(UTC)
    return parsed.replace(tzinfo=UTC)


def _pdf_timezone_offset(value: str) -> timezone | None:
    sign = 1 if value[0] == "+" else -1
    digits = "".join(character for character in value[1:] if character.isdigit())
    if len(digits) < MIN_PDF_TIMEZONE_DIGITS:
        return None
    hours = int(digits[:MIN_PDF_TIMEZONE_DIGITS])
    minutes = int(digits[2:4] or "0")
    return timezone(timedelta(hours=sign * hours, minutes=sign * minutes))


def _aware_datetime(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _iso_datetime(value: datetime | None) -> str | None:
    aware = _aware_datetime(value)
    return aware.isoformat() if aware else None


def _json_value(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.hex()
    if isinstance(value, datetime):
        return _iso_datetime(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, tuple | list):
        return [_json_value(item) for item in value]
    return str(value)
