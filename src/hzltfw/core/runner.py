from collections.abc import Iterable

from sqlmodel import Session, select

from hzltfw.core.exceptions import EvidenceNotFoundError
from hzltfw.core.models import Artifact, EvidenceFile, EvidenceItem, PluginRun
from hzltfw.core.plugin import (
    ArtifactCreate,
    BasePlugin,
    PluginContext,
)
from hzltfw.core.workspace import case_workspace_path
from hzltfw.plugins.archive_index import ArchiveIndexPlugin
from hzltfw.plugins.file_type import FileTypePlugin
from hzltfw.plugins.hash_manifest import HashManifestPlugin
from hzltfw.plugins.keyword_search import KeywordSearchPlugin
from hzltfw.plugins.metadata_extract import MetadataExtractPlugin
from hzltfw.utils.timestamps import utc_now


def default_plugins() -> list[BasePlugin]:
    return [
        HashManifestPlugin(),
        FileTypePlugin(),
        KeywordSearchPlugin(),
        ArchiveIndexPlugin(),
        MetadataExtractPlugin(),
    ]


def run_plugins_for_evidence(
    session: Session,
    evidence_id: int,
    plugins: Iterable[BasePlugin] | None = None,
) -> list[PluginRun]:
    evidence = session.get(EvidenceItem, evidence_id)
    if evidence is None:
        raise EvidenceNotFoundError

    indexed_files = list(
        session.exec(
            select(EvidenceFile).where(EvidenceFile.evidence_id == evidence_id),
        ),
    )
    selected_plugins = list(plugins or default_plugins())
    runs: list[PluginRun] = []

    for plugin in selected_plugins:
        run = PluginRun(
            case_id=evidence.case_id,
            evidence_id=evidence.id,
            plugin_name=plugin.name,
            plugin_version=plugin.version,
            status="running",
        )
        session.add(run)
        session.commit()
        session.refresh(run)

        context = PluginContext(
            case_id=evidence.case_id,
            evidence_id=evidence.id or 0,
            workspace_path=case_workspace_path(evidence.case_id),
            plugin_run_id=run.id or 0,
        )

        try:
            artifacts = _run_plugin(plugin, context, evidence, indexed_files)
            session.add_all(
                _to_artifact(
                    create=artifact,
                    case_id=evidence.case_id,
                    evidence_id=evidence.id,
                    plugin_run_id=run.id or 0,
                )
                for artifact in artifacts
            )
            _apply_artifact_side_effects(indexed_files, artifacts)
            run.status = "success"
        except Exception as exc:  # noqa: BLE001
            run.status = "failed"
            run.error_message = str(exc)
        finally:
            run.finished_at = utc_now()
            session.add(run)
            session.commit()
            session.refresh(run)
            runs.append(run)

    return runs


def _run_plugin(
    plugin: BasePlugin,
    context: PluginContext,
    evidence: EvidenceItem,
    files: list[EvidenceFile],
) -> list[ArtifactCreate]:
    if plugin.plugin_type == "evidence":
        evidence_plugin = plugin  # type: EvidencePlugin
        return evidence_plugin.analyze_evidence(context, evidence, files)

    file_plugin = plugin  # type: FilePlugin
    artifacts: list[ArtifactCreate] = []
    for file in files:
        if file_plugin.supports(file):
            artifacts.extend(file_plugin.analyze_file(context, evidence, file))
    return artifacts


def _to_artifact(
    create: ArtifactCreate,
    case_id: int,
    evidence_id: int | None,
    plugin_run_id: int,
) -> Artifact:
    return Artifact(
        case_id=case_id,
        evidence_id=evidence_id,
        plugin_run_id=plugin_run_id,
        artifact_type=create.artifact_type,
        title=create.title,
        summary=create.summary,
        source_path=create.source_path,
        timestamp=create.timestamp,
        severity=create.severity,
        is_key=create.is_key,
        tags_json=create.tags,
        data_json=create.data,
    )


def _apply_artifact_side_effects(
    indexed_files: list[EvidenceFile],
    artifacts: list[ArtifactCreate],
) -> None:
    for artifact in artifacts:
        if artifact.artifact_type == "hash.manifest":
            _apply_hash_manifest(indexed_files, artifact)


def _apply_hash_manifest(
    indexed_files: list[EvidenceFile],
    artifact: ArtifactCreate,
) -> None:
    manifest_files = artifact.data.get("files")
    if not isinstance(manifest_files, list):
        return

    files_by_path = {file.relative_path: file for file in indexed_files}
    for entry in manifest_files:
        if not isinstance(entry, dict):
            continue
        relative_path = entry.get("relative_path")
        sha256 = entry.get("sha256")
        if not isinstance(relative_path, str) or not isinstance(sha256, str):
            continue
        indexed_file = files_by_path.get(relative_path)
        if indexed_file is not None:
            indexed_file.sha256 = sha256
