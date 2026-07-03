from pathlib import Path
from typing import Any

import puremagic

from hzltfw.core.models import EvidenceFile, EvidenceItem
from hzltfw.core.plugin import ArtifactCreate, PluginContext


class FileTypePlugin:
    name = "file_type"
    version = "1.0.0"
    description = "Identify file types from magic bytes and flag extension mismatch."
    plugin_type = "file"
    artifact_types = ["file.type_mismatch"]

    def supports(self, file: EvidenceFile) -> bool:
        return not file.is_virtual and file.absolute_path is not None

    def analyze_file(
        self,
        context: PluginContext,
        evidence: EvidenceItem,
        file: EvidenceFile,
    ) -> list[ArtifactCreate]:
        del context, evidence

        candidates = _detect_candidates(Path(file.absolute_path or ""))
        if not candidates:
            return []

        best = candidates[0]
        detected_extensions = {
            candidate["extension"]
            for candidate in candidates
            if candidate.get("extension")
        }
        mismatch = bool(
            file.extension
            and detected_extensions
            and file.extension not in detected_extensions,
        )
        if not mismatch:
            return []

        return [
            ArtifactCreate(
                artifact_type="file.type_mismatch",
                title="Extension does not match detected type",
                summary=(
                    f"{file.relative_path} uses extension {file.extension}, "
                    f"but magic bytes suggest {best.get('extension') or 'unknown'}."
                ),
                source_path=file.relative_path,
                timestamp=file.mtime,
                severity="medium",
                is_key=True,
                tags=["file_type", "mismatch", "suspicious"],
                data={
                    "extension": file.extension,
                    "detected_extension": best.get("extension"),
                    "detected_mime": best.get("mime_type"),
                    "detected_name": best.get("name"),
                    "candidate_extensions": sorted(detected_extensions),
                },
            )
        ]


def _detect_candidates(path: Path) -> list[dict[str, Any]]:
    try:
        matches = puremagic.magic_file(str(path))
    except puremagic.PureError:
        return []

    candidates = [
        {
            "extension": match.extension,
            "mime_type": match.mime_type or None,
            "name": match.name,
            "confidence": match.confidence,
        }
        for match in matches
    ]
    return sorted(
        candidates,
        key=lambda candidate: candidate["confidence"] or 0,
        reverse=True,
    )
