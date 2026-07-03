from collections import defaultdict
from pathlib import Path
from shutil import copytree

from sqlmodel import Session, select

from hzltfw.core.exceptions import CaseNotFoundError
from hzltfw.core.models import Artifact, Case, EvidenceFile, EvidenceItem, PluginRun
from hzltfw.utils.i18n import current_language, t


def export_case_markdown(
    session: Session,
    case_id: int,
    output_path: str | Path,
    *,
    include_manifest: bool = False,
) -> Path:
    case = session.get(Case, case_id)
    if case is None:
        raise CaseNotFoundError

    evidence_items = list(
        session.exec(select(EvidenceItem).where(EvidenceItem.case_id == case_id)),
    )
    runs = list(session.exec(select(PluginRun).where(PluginRun.case_id == case_id)))
    artifacts = list(session.exec(select(Artifact).where(Artifact.case_id == case_id)))

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    report = _render_report(
        case=case,
        evidence_items=evidence_items,
        runs=runs,
        artifacts=artifacts,
        appendix=_render_appendix(
            _render_manifest(session, evidence_items) if include_manifest else [],
            [],
            current_language(),
        ),
        language=current_language(),
    )
    output.write_text(
        report,
        encoding="utf-8",
    )
    return output


def export_case_report_bundle(
    session: Session,
    case_id: int,
    output_dir: str | Path,
    *,
    include_manifest: bool = False,
) -> Path:
    case = session.get(Case, case_id)
    if case is None:
        raise CaseNotFoundError

    evidence_items = list(
        session.exec(select(EvidenceItem).where(EvidenceItem.case_id == case_id)),
    )
    runs = list(session.exec(select(PluginRun).where(PluginRun.case_id == case_id)))
    artifacts = list(session.exec(select(Artifact).where(Artifact.case_id == case_id)))

    bundle_root = Path(output_dir)
    bundle_root.mkdir(parents=True, exist_ok=True)
    external_links = _copy_external_reports(bundle_root, artifacts)
    language = current_language()
    report = _render_report(
        case=case,
        evidence_items=evidence_items,
        runs=runs,
        artifacts=artifacts,
        appendix=_render_appendix(
            _render_manifest(session, evidence_items) if include_manifest else [],
            external_links,
            language,
        ),
        language=language,
    )
    report_path = bundle_root / "report.md"
    report_path.write_text(report, encoding="utf-8")
    return report_path


def _render_report(  # noqa: PLR0913
    case: Case,
    evidence_items: list[EvidenceItem],
    runs: list[PluginRun],
    artifacts: list[Artifact],
    appendix: list[str],
    language: str,
) -> str:
    lines = [
        f"# {t('report.title', language=language)}",
        "",
    ]
    lines.extend(_render_case_info(case, language))
    lines.extend(_render_evidence_info(evidence_items, language))
    lines.extend(_render_run_records(runs, language))
    lines.extend(_render_key_findings(artifacts, language))
    lines.extend(_render_timeline(artifacts, language))
    lines.extend(_render_detailed_results(artifacts, language))
    lines.extend(appendix)
    return "\n".join(lines).rstrip() + "\n"


def _render_case_info(case: Case, language: str) -> list[str]:
    return [
        f"## 1. {t('report.case_info', language=language)}",
        "",
        f"- Case No: {case.case_no}",
        f"- Name: {case.name}",
        f"- Investigator: {case.investigator or 'N/A'}",
        f"- Created At: {case.created_at.isoformat()}",
        f"- Description: {case.description or 'N/A'}",
        "",
    ]


def _render_evidence_info(
    evidence_items: list[EvidenceItem],
    language: str,
) -> list[str]:
    lines = [f"## 2. {t('report.evidence_info', language=language)}", ""]
    for evidence in evidence_items:
        lines.extend(
            [
                f"### {evidence.name}",
                "",
                f"- Type: {evidence.evidence_type}",
                f"- Source: `{evidence.source_path}`",
                f"- Added At: {evidence.added_at.isoformat()}",
                f"- Size: {evidence.size_bytes} bytes",
                "",
            ],
        )
    return lines


def _render_run_records(runs: list[PluginRun], language: str) -> list[str]:
    lines = [f"## 3. {t('report.run_records', language=language)}", ""]
    for run in runs:
        finished_at = run.finished_at.isoformat() if run.finished_at else "N/A"
        lines.extend(
            [
                f"- {run.plugin_name} {run.plugin_version}: {run.status}",
                f"  - Started: {run.started_at.isoformat()}",
                f"  - Finished: {finished_at}",
                f"  - Error: {run.error_message or 'N/A'}",
            ],
        )
    return lines


def _render_key_findings(artifacts: list[Artifact], language: str) -> list[str]:
    key_findings = [
        artifact
        for artifact in artifacts
        if artifact.is_key or artifact.severity != "info"
    ]
    lines = ["", f"## 4. {t('report.key_findings', language=language)}", ""]
    if key_findings:
        for artifact in key_findings:
            lines.append(_artifact_bullet(artifact))
    else:
        lines.append(t("report.no_key", language=language))
    return lines


def _render_timeline(artifacts: list[Artifact], language: str) -> list[str]:
    timeline = sorted(
        (artifact for artifact in artifacts if artifact.timestamp is not None),
        key=lambda artifact: artifact.timestamp,
    )
    lines = ["", f"## 5. {t('report.timeline', language=language)}", ""]
    if timeline:
        for artifact in timeline:
            lines.append(
                f"- {artifact.timestamp.isoformat()} | "
                f"{artifact.artifact_type} | {artifact.title}",
            )
    else:
        lines.append(t("report.no_timeline", language=language))
    return lines


def _render_detailed_results(artifacts: list[Artifact], language: str) -> list[str]:
    lines = ["", f"## 6. {t('report.details', language=language)}", ""]
    grouped: dict[str, list[Artifact]] = defaultdict(list)
    for artifact in artifacts:
        grouped[artifact.artifact_type].append(artifact)

    for artifact_type, group in sorted(grouped.items()):
        lines.extend([f"### {artifact_type}", ""])
        for artifact in group:
            lines.append(_artifact_bullet(artifact))
        lines.append("")
    return lines


def _render_appendix(
    manifest: list[str],
    external_links: list[str],
    language: str,
) -> list[str]:
    lines = [f"## 7. {t('report.appendix', language=language)}", ""]
    if external_links:
        lines.extend([f"### {t('report.external', language=language)}", ""])
        lines.extend(external_links)
        lines.append("")
    if manifest:
        lines.extend(manifest)
    else:
        lines.append(t("report.no_manifest", language=language))
    return lines


def _artifact_bullet(artifact: Artifact) -> str:
    source = f" `{artifact.source_path}`" if artifact.source_path else ""
    return (
        f"- [{artifact.severity}] {artifact.title}{source}: "
        f"{artifact.summary or 'No summary'}"
    )


def _render_manifest(session: Session, evidence_items: list[EvidenceItem]) -> list[str]:
    lines = [f"### {t('report.manifest')}", ""]
    for evidence in evidence_items:
        files = list(
            session.exec(
                select(EvidenceFile).where(EvidenceFile.evidence_id == evidence.id),
            ),
        )
        lines.extend(
            [
                f"#### {evidence.name}",
                "",
                "| Path | Size | SHA256 |",
                "| --- | ---: | --- |",
            ],
        )
        for file in files:
            lines.append(
                f"| `{file.relative_path}` | {file.size_bytes} | {file.sha256 or ''} |",
            )
        lines.append("")
    return lines


def _copy_external_reports(bundle_root: Path, artifacts: list[Artifact]) -> list[str]:
    links: list[str] = []
    for artifact in artifacts:
        if artifact.artifact_type != "external.report":
            continue
        output_dir = artifact.data_json.get("output_dir")
        if not isinstance(output_dir, str):
            continue
        source_dir = Path(output_dir)
        if not source_dir.exists() or not source_dir.is_dir():
            continue
        tool_name = str(artifact.data_json.get("tool_name") or "external")
        destination = (
            bundle_root / "external" / tool_name / f"run-{artifact.plugin_run_id}"
        )
        copytree(source_dir, destination, dirs_exist_ok=True)
        links.append(_external_report_link(artifact, bundle_root, destination))
    return links


def _external_report_link(
    artifact: Artifact,
    bundle_root: Path,
    destination: Path,
) -> str:
    report_path = artifact.data_json.get("report_path")
    link_target = destination
    if isinstance(report_path, str):
        source_report = Path(report_path)
        try:
            relative_report = source_report.relative_to(
                Path(artifact.data_json["output_dir"]),
            )
        except (KeyError, ValueError):
            relative_report = Path(source_report.name)
        link_target = destination / relative_report
    relative_link = link_target.relative_to(bundle_root).as_posix()
    title = artifact.title.replace("[", "\\[").replace("]", "\\]")
    return f"- [{title}]({relative_link})"
