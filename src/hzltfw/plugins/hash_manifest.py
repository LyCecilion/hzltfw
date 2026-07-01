from hzltfw.core.models import EvidenceFile, EvidenceItem
from hzltfw.core.plugin import ArtifactCreate, PluginContext
from hzltfw.utils.hashing import hash_file


class HashManifestPlugin:
    name = "hash_manifest"
    version = "0.1.0"
    description = "Generate MD5/SHA1/SHA256 hashes for indexed evidence files."
    plugin_type = "evidence"
    artifact_types = ["hash.manifest"]

    def analyze_evidence(
        self,
        context: PluginContext,
        evidence: EvidenceItem,
        files: list[EvidenceFile],
    ) -> list[ArtifactCreate]:
        manifest: list[dict[str, object]] = []
        total_size = 0

        for file in files:
            if file.is_virtual or not file.absolute_path:
                continue
            hashes = hash_file(file.absolute_path)
            total_size += file.size_bytes
            manifest.append(
                {
                    "relative_path": file.relative_path,
                    "virtual_path": file.virtual_path,
                    "size_bytes": file.size_bytes,
                    "mtime": file.mtime.isoformat() if file.mtime else None,
                    "ctime": file.ctime.isoformat() if file.ctime else None,
                    **hashes,
                },
            )

        return [
            ArtifactCreate(
                artifact_type="hash.manifest",
                title="Evidence hash manifest",
                summary=(
                    f"Generated MD5/SHA1/SHA256 hashes for {len(manifest)} files "
                    f"in evidence '{evidence.name}'."
                ),
                severity="info",
                tags=["hash", "manifest"],
                data={
                    "case_id": context.case_id,
                    "evidence_id": context.evidence_id,
                    "file_count": len(manifest),
                    "total_size_bytes": total_size,
                    "files": manifest,
                },
            ),
        ]
