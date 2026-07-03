from dataclasses import dataclass, field
from pathlib import Path

from hzltfw.utils.timestamps import utc_now


@dataclass(frozen=True)
class HandoffItem:
    category: str
    paths: list[str]
    purpose: str
    plugins: list[str] = field(default_factory=list)
    notes: str = ""


WINDOWS_HANDOFF_ITEMS = [
    HandoffItem(
        category="User documents and desktop",
        paths=[
            r"Users\<user>\Documents",
            r"Users\<user>\Desktop",
            r"Users\<user>\Downloads",
        ],
        purpose=(
            "Collect ordinary user-created files, downloads, archives, and documents."
        ),
        plugins=["hash_manifest", "file_type", "keyword_search", "metadata_extract"],
    ),
    HandoffItem(
        category="Chromium profile",
        paths=[
            r"Users\<user>\AppData\Local\Google\Chrome\User Data\Default\History",
            r"Users\<user>\AppData\Local\Microsoft\Edge\User Data\Default\History",
        ],
        purpose="Preserve browser visit and download history for optional parsing.",
        plugins=["browser_history"],
        notes="Bonus path; do not block the MVP demo on this artifact.",
    ),
    HandoffItem(
        category="Recent shortcuts",
        paths=[r"Users\<user>\AppData\Roaming\Microsoft\Windows\Recent"],
        purpose="Collect LNK shortcuts that can indicate recently opened files.",
        plugins=["lnk_parser"],
        notes="Future plugin target.",
    ),
    HandoffItem(
        category="Registry hives",
        paths=[
            r"Users\<user>\NTUSER.DAT",
            r"Windows\System32\config\SOFTWARE",
            r"Windows\System32\config\SYSTEM",
        ],
        purpose="Collect user and system registry hives for recent activity review.",
        plugins=["registry_quicklook"],
        notes="Future plugin target; export the hive files as-is.",
    ),
    HandoffItem(
        category="Windows event logs",
        paths=[r"Windows\System32\winevt\Logs\*.evtx"],
        purpose="Collect login, system, service, and device event logs.",
        plugins=["evtx_summary"],
        notes="Future plugin target; keep original EVTX files.",
    ),
    HandoffItem(
        category="Recycle Bin",
        paths=[r"$Recycle.Bin"],
        purpose="Collect deleted-file metadata and recoverable deleted content.",
        plugins=["recycle_bin"],
        notes="Future plugin target; preserve SID subdirectories.",
    ),
    HandoffItem(
        category="Email and office files",
        paths=[
            r"Users\<user>\Documents\*.docx",
            r"Users\<user>\Documents\*.xlsx",
            r"Users\<user>\Documents\*.pptx",
            r"Users\<user>\Documents\*.msg",
        ],
        purpose="Collect documents and messages that may contain leakage evidence.",
        plugins=["metadata_extract", "email_msg", "office_suspicious"],
    ),
]


def render_handoff_markdown(
    *,
    case_name: str = "",
    operator: str = "",
    source_image: str = "",
    sample_sha256: str = "",
    items: list[HandoffItem] | None = None,
) -> str:
    selected_items = items or WINDOWS_HANDOFF_ITEMS
    lines = [
        "# Windows Evidence Handoff Checklist",
        "",
        "This checklist is for exporting files from a Windows image, E01, or mounted "
        "forensic source before importing the exported directory into hzltfw.",
        "",
        "hzltfw analyzes exported files and directories. It does not directly parse "
        "E01 images, partition tables, or NTFS filesystems in the MVP workflow.",
        "",
        "## Case",
        "",
        f"- Case: {case_name or 'N/A'}",
        f"- Operator: {operator or 'N/A'}",
        f"- Source image: {source_image or 'N/A'}",
        f"- Sample SHA256: {sample_sha256 or 'N/A'}",
        f"- Generated at: {utc_now().isoformat()}",
        "",
        "## Export Rules",
        "",
        "- Use a dedicated forensic tool to mount, browse, or export the source image.",
        "- Export files into a normal directory before importing them into hzltfw.",
        "- Preserve original filenames and directory structure when possible.",
        "- Do not include real personal data in course demonstration samples.",
        "- Record hashes for shared sample archives outside the repository.",
        "",
        "## Checklist",
        "",
    ]

    for index, item in enumerate(selected_items, start=1):
        lines.extend(_render_item(index, item))

    return "\n".join(lines).rstrip() + "\n"


def export_handoff_markdown(
    output_path: str | Path,
    *,
    case_name: str = "",
    operator: str = "",
    source_image: str = "",
    sample_sha256: str = "",
) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        render_handoff_markdown(
            case_name=case_name,
            operator=operator,
            source_image=source_image,
            sample_sha256=sample_sha256,
        ),
        encoding="utf-8",
    )
    return output


def handoff_table_rows() -> list[dict[str, str]]:
    return [
        {
            "category": item.category,
            "paths": "\n".join(item.paths),
            "purpose": item.purpose,
            "plugins": ", ".join(item.plugins) if item.plugins else "N/A",
        }
        for item in WINDOWS_HANDOFF_ITEMS
    ]


def _render_item(index: int, item: HandoffItem) -> list[str]:
    lines = [
        f"### {index}. {item.category}",
        "",
        f"- Purpose: {item.purpose}",
        f"- Related plugins: {', '.join(item.plugins) if item.plugins else 'N/A'}",
    ]
    if item.notes:
        lines.append(f"- Notes: {item.notes}")
    lines.extend(["", "Paths:"])
    lines.extend(f"- `{path}`" for path in item.paths)
    lines.append("")
    return lines
