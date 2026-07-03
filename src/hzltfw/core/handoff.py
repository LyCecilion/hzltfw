from dataclasses import dataclass, field
from fnmatch import fnmatch
from pathlib import Path

from hzltfw.utils.timestamps import utc_now

MAX_FINDINGS_PER_TARGET = 50


@dataclass(frozen=True)
class HandoffTarget:
    category: str
    display_paths: list[str]
    match_patterns: list[str]
    purpose: str
    plugins: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass(frozen=True)
class IntakeFinding:
    category: str
    relative_path: str
    kind: str
    matched_pattern: str
    size_bytes: int | None = None


@dataclass(frozen=True)
class IntakeResult:
    root_path: Path
    findings: list[IntakeFinding]
    missing_categories: list[str]


WINDOWS_HANDOFF_TARGETS = [
    HandoffTarget(
        category="User documents and desktop",
        display_paths=[
            r"Users\<user>\Documents",
            r"Users\<user>\Desktop",
            r"Users\<user>\Downloads",
        ],
        match_patterns=[
            "users/*/documents",
            "users/*/documents/**",
            "users/*/desktop",
            "users/*/desktop/**",
            "users/*/downloads",
            "users/*/downloads/**",
        ],
        purpose=(
            "Find ordinary user-created files, downloads, archives, and documents."
        ),
        plugins=["hash_manifest", "file_type", "keyword_search", "metadata_extract"],
    ),
    HandoffTarget(
        category="Chromium profile",
        display_paths=[
            r"Users\<user>\AppData\Local\Google\Chrome\User Data\Default\History",
            r"Users\<user>\AppData\Local\Microsoft\Edge\User Data\Default\History",
        ],
        match_patterns=[
            "users/*/appdata/local/google/chrome/user data/*/history",
            "users/*/appdata/local/microsoft/edge/user data/*/history",
        ],
        purpose="Find browser visit and download history databases.",
        plugins=["browser_history"],
        notes="Bonus path; do not block the MVP demo on this artifact.",
    ),
    HandoffTarget(
        category="Recent shortcuts",
        display_paths=[r"Users\<user>\AppData\Roaming\Microsoft\Windows\Recent"],
        match_patterns=[
            "users/*/appdata/roaming/microsoft/windows/recent",
            "users/*/appdata/roaming/microsoft/windows/recent/**",
            "users/*/appdata/roaming/microsoft/windows/recent/*.lnk",
        ],
        purpose="Find LNK shortcuts that can indicate recently opened files.",
        plugins=["lnk_parser"],
        notes="Future plugin target.",
    ),
    HandoffTarget(
        category="Registry hives",
        display_paths=[
            r"Users\<user>\NTUSER.DAT",
            r"Windows\System32\config\SOFTWARE",
            r"Windows\System32\config\SYSTEM",
        ],
        match_patterns=[
            "users/*/ntuser.dat",
            "windows/system32/config/software",
            "windows/system32/config/system",
        ],
        purpose="Find user and system registry hives for recent activity review.",
        plugins=["registry_quicklook"],
        notes="Future plugin target; import hive files as-is.",
    ),
    HandoffTarget(
        category="Windows event logs",
        display_paths=[r"Windows\System32\winevt\Logs\*.evtx"],
        match_patterns=["windows/system32/winevt/logs/*.evtx"],
        purpose="Find login, system, service, and device event logs.",
        plugins=["evtx_summary"],
        notes="Future plugin target; keep original EVTX files.",
    ),
    HandoffTarget(
        category="Recycle Bin",
        display_paths=[r"$Recycle.Bin"],
        match_patterns=["$recycle.bin", "$recycle.bin/**"],
        purpose="Find deleted-file metadata and recoverable deleted content.",
        plugins=["recycle_bin"],
        notes="Future plugin target; preserve SID subdirectories.",
    ),
    HandoffTarget(
        category="Email and office files",
        display_paths=[
            r"Users\<user>\Documents\*.docx",
            r"Users\<user>\Documents\*.xlsx",
            r"Users\<user>\Documents\*.pptx",
            r"Users\<user>\Documents\*.msg",
        ],
        match_patterns=[
            "users/*/documents/*.docx",
            "users/*/documents/*.xlsx",
            "users/*/documents/*.pptx",
            "users/*/documents/*.msg",
            "users/*/documents/**/*.docx",
            "users/*/documents/**/*.xlsx",
            "users/*/documents/**/*.pptx",
            "users/*/documents/**/*.msg",
            "users/*/desktop/*.docx",
            "users/*/desktop/**/*.docx",
            "users/*/downloads/*.msg",
            "users/*/downloads/**/*.msg",
        ],
        purpose="Find documents and messages that may contain leakage evidence.",
        plugins=["metadata_extract", "email_msg", "office_suspicious"],
    ),
]


def scan_exported_directory(
    root_path: str | Path,
    *,
    targets: list[HandoffTarget] | None = None,
) -> IntakeResult:
    root = Path(root_path).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise NotADirectoryError(root)

    selected_targets = targets or WINDOWS_HANDOFF_TARGETS
    findings: list[IntakeFinding] = []
    categories_with_findings: set[str] = set()
    per_category_counts: dict[str, int] = {}

    for path in sorted(root.rglob("*")):
        relative_path = path.relative_to(root).as_posix()
        normalized_path = relative_path.lower()
        for target in selected_targets:
            matched_pattern = _matched_pattern(normalized_path, target.match_patterns)
            if matched_pattern is None:
                continue
            categories_with_findings.add(target.category)
            count = per_category_counts.get(target.category, 0)
            if count >= MAX_FINDINGS_PER_TARGET:
                continue
            per_category_counts[target.category] = count + 1
            findings.append(
                IntakeFinding(
                    category=target.category,
                    relative_path=relative_path,
                    kind="directory" if path.is_dir() else "file",
                    matched_pattern=matched_pattern,
                    size_bytes=path.stat().st_size if path.is_file() else None,
                ),
            )

    return IntakeResult(
        root_path=root,
        findings=findings,
        missing_categories=[
            target.category
            for target in selected_targets
            if target.category not in categories_with_findings
        ],
    )


def render_handoff_markdown(  # noqa: PLR0913
    *,
    case_name: str = "",
    operator: str = "",
    source_image: str = "",
    sample_sha256: str = "",
    exported_root: str | Path | None = None,
    targets: list[HandoffTarget] | None = None,
) -> str:
    selected_targets = targets or WINDOWS_HANDOFF_TARGETS
    result = (
        scan_exported_directory(exported_root, targets=selected_targets)
        if exported_root
        else None
    )
    lines = [
        "# Windows Evidence Intake Checklist",
        "",
        "Use a forensic tool to export selected files from a Windows image, E01, "
        "or mounted source into a normal directory. hzltfw then inspects that "
        "exported directory and analyzes its files.",
        "",
        "hzltfw does not directly parse E01 images, partition tables, or NTFS "
        "filesystems in the MVP workflow.",
        "",
        "## Case",
        "",
        f"- Case: {case_name or 'N/A'}",
        f"- Operator: {operator or 'N/A'}",
        f"- Source image: {source_image or 'N/A'}",
        f"- Sample SHA256: {sample_sha256 or 'N/A'}",
        f"- Exported root: {result.root_path if result else 'N/A'}",
        f"- Generated at: {utc_now().isoformat()}",
        "",
        "## Intake Result",
        "",
    ]

    if result:
        lines.extend(_render_intake_result(result))
    else:
        lines.append("No exported directory was inspected.")
        lines.append("")

    lines.extend(["## Expected Sources", ""])
    for index, target in enumerate(selected_targets, start=1):
        lines.extend(_render_target(index, target))

    return "\n".join(lines).rstrip() + "\n"


def export_handoff_markdown(  # noqa: PLR0913
    output_path: str | Path,
    *,
    case_name: str = "",
    operator: str = "",
    source_image: str = "",
    sample_sha256: str = "",
    exported_root: str | Path | None = None,
) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        render_handoff_markdown(
            case_name=case_name,
            operator=operator,
            source_image=source_image,
            sample_sha256=sample_sha256,
            exported_root=exported_root,
        ),
        encoding="utf-8",
    )
    return output


def handoff_table_rows() -> list[dict[str, str]]:
    return [
        {
            "category": target.category,
            "paths": "\n".join(target.display_paths),
            "purpose": target.purpose,
            "plugins": ", ".join(target.plugins) if target.plugins else "N/A",
        }
        for target in WINDOWS_HANDOFF_TARGETS
    ]


def intake_table_rows(result: IntakeResult) -> list[dict[str, str | int]]:
    return [
        {
            "category": finding.category,
            "path": finding.relative_path,
            "kind": finding.kind,
            "size": finding.size_bytes if finding.size_bytes is not None else "",
        }
        for finding in result.findings
    ]


def missing_table_rows(result: IntakeResult) -> list[dict[str, str]]:
    return [{"category": category} for category in result.missing_categories]


def _matched_pattern(path: str, patterns: list[str]) -> str | None:
    return next((pattern for pattern in patterns if fnmatch(path, pattern)), None)


def _render_intake_result(result: IntakeResult) -> list[str]:
    lines = [
        f"- Findings: {len(result.findings)}",
        f"- Missing source categories: {len(result.missing_categories)}",
        "",
    ]
    if result.findings:
        lines.extend(["### Found Sources", ""])
        for finding in result.findings:
            size = (
                f", {finding.size_bytes} bytes"
                if finding.size_bytes is not None
                else ""
            )
            lines.append(
                f"- {finding.category}: `{finding.relative_path}` "
                f"({finding.kind}{size})",
            )
        lines.append("")
    if result.missing_categories:
        lines.extend(["### Missing Typical Sources", ""])
        lines.extend(f"- {category}" for category in result.missing_categories)
        lines.append("")
    return lines


def _render_target(index: int, target: HandoffTarget) -> list[str]:
    lines = [
        f"### {index}. {target.category}",
        "",
        f"- Purpose: {target.purpose}",
        f"- Related plugins: {', '.join(target.plugins) if target.plugins else 'N/A'}",
    ]
    if target.notes:
        lines.append(f"- Notes: {target.notes}")
    lines.extend(["", "Expected paths:"])
    lines.extend(f"- `{path}`" for path in target.display_paths)
    lines.append("")
    return lines
