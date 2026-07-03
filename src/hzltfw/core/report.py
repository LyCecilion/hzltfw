from collections import defaultdict
from pathlib import Path
from shutil import copytree

from sqlmodel import Session, select

from hzltfw.core.exceptions import CaseNotFoundError
from hzltfw.core.models import Artifact, Case, EvidenceFile, EvidenceItem, PluginRun


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
        ),
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
    report = _render_report(
        case=case,
        evidence_items=evidence_items,
        runs=runs,
        artifacts=artifacts,
        appendix=_render_appendix(
            _render_manifest(session, evidence_items) if include_manifest else [],
            external_links,
        ),
    )
    report_path = bundle_root / "report.md"
    report_path.write_text(report, encoding="utf-8")
    return report_path


def _render_report(
    case: Case,
    evidence_items: list[EvidenceItem],
    runs: list[PluginRun],
    artifacts: list[Artifact],
    appendix: list[str],
) -> str:
    lines = [
        "# Electronic Data Forensics Analysis Report",
        "",
    ]
    lines.extend(_render_case_info(case))
    lines.extend(_render_evidence_info(evidence_items))
    lines.extend(_render_run_records(runs))
    lines.extend(_render_key_findings(artifacts))
    lines.extend(_render_timeline(artifacts))
    lines.extend(_render_detailed_results(artifacts))
    lines.extend(appendix)
    return "\n".join(lines).rstrip() + "\n"


def _render_case_info(case: Case) -> list[str]:
    return [
        "## 1. Case Information",
        "",
        f"- Case No: {case.case_no}",
        f"- Name: {case.name}",
        f"- Investigator: {case.investigator or 'N/A'}",
        f"- Created At: {case.created_at.isoformat()}",
        f"- Description: {case.description or 'N/A'}",
        "",
    ]


def _render_evidence_info(evidence_items: list[EvidenceItem]) -> list[str]:
    lines = ["## 2. Evidence Information", ""]
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


def _render_run_records(runs: list[PluginRun]) -> list[str]:
    lines = ["## 3. Tool Run Records", ""]
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


def _render_key_findings(artifacts: list[Artifact]) -> list[str]:
    key_findings = [
        artifact
        for artifact in artifacts
        if artifact.is_key or artifact.severity != "info"
    ]
    lines = ["", "## 4. Key Findings", ""]
    if key_findings:
        for artifact in key_findings:
            lines.append(_artifact_bullet(artifact))
    else:
        lines.append("No key findings were marked.")
    return lines


def _render_timeline(artifacts: list[Artifact]) -> list[str]:
    timeline = sorted(
        (artifact for artifact in artifacts if artifact.timestamp is not None),
        key=lambda artifact: artifact.timestamp,
    )
    lines = ["", "## 5. Timeline", ""]
    if timeline:
        for artifact in timeline:
            lines.append(
                f"- {artifact.timestamp.isoformat()} | "
                f"{artifact.artifact_type} | {artifact.title}",
        )
    else:
        lines.append("No timestamped artifacts.")
    return lines


def _render_detailed_results(artifacts: list[Artifact]) -> list[str]:
    lines = ["", "## 6. Detailed Results", ""]
    grouped: dict[str, list[Artifact]] = defaultdict(list)
    for artifact in artifacts:
        grouped[artifact.artifact_type].append(artifact)

    for artifact_type, group in sorted(grouped.items()):
        lines.extend([f"### {artifact_type}", ""])
        for artifact in group:
            lines.append(_artifact_bullet(artifact))
        lines.append("")
    return lines


def _render_appendix(manifest: list[str], external_links: list[str]) -> list[str]:
    lines = ["## 7. Appendix", ""]
    if external_links:
        lines.extend(["### External Tool Reports", ""])
        lines.extend(external_links)
        lines.append("")
    if manifest:
        lines.extend(manifest)
    else:
        lines.append("Full file manifest was not included.")
    return lines


def _artifact_bullet(artifact: Artifact) -> str:
    source = f" `{artifact.source_path}`" if artifact.source_path else ""
    return (
        f"- [{artifact.severity}] {artifact.title}{source}: "
        f"{artifact.summary or 'No summary'}"
    )


def _render_manifest(session: Session, evidence_items: list[EvidenceItem]) -> list[str]:
    lines = ["### Full File Manifest", ""]
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
            bundle_root
            / "external"
            / tool_name
            / f"run-{artifact.plugin_run_id}"
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
