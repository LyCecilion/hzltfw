from pathlib import Path

from hzltfw.core.handoff import (
    export_handoff_markdown,
    render_handoff_markdown,
    scan_exported_directory,
)


def test_scan_exported_directory_finds_windows_sources(tmp_path: Path) -> None:
    exported = _write_exported_windows_tree(tmp_path)

    result = scan_exported_directory(exported)

    found_categories = {finding.category for finding in result.findings}
    assert "User documents and desktop" in found_categories
    assert "Chromium profile" in found_categories
    assert "Registry hives" in found_categories
    assert "Windows event logs" in found_categories
    assert "Recent shortcuts" in found_categories
    assert "Recycle Bin" in found_categories
    assert "Email and office files" in found_categories


def test_render_handoff_markdown_includes_intake_result(tmp_path: Path) -> None:
    exported = _write_exported_windows_tree(tmp_path)

    markdown = render_handoff_markdown(
        case_name="Demo Case",
        operator="tester",
        source_image="sample.E01",
        sample_sha256="abc123",
        exported_root=exported,
    )

    assert "Windows Evidence Intake Checklist" in markdown
    assert "sample.E01" in markdown
    assert "Found Sources" in markdown
    assert "Users/Alice/Documents/leak.docx" in markdown
    assert "Windows\\System32\\winevt\\Logs\\*.evtx" in markdown
    assert "hzltfw does not directly parse E01 images" in markdown


def test_export_handoff_markdown(tmp_path: Path) -> None:
    exported = _write_exported_windows_tree(tmp_path)
    output = export_handoff_markdown(
        tmp_path / "handoff.md",
        case_name="CASE-001",
        exported_root=exported,
    )

    assert output.exists()
    text = output.read_text(encoding="utf-8")
    assert "CASE-001" in text
    assert "Users/Alice/NTUSER.DAT" in text


def _write_exported_windows_tree(tmp_path: Path) -> Path:
    root = tmp_path / "exported"
    user = root / "Users" / "Alice"
    (user / "Documents").mkdir(parents=True)
    (user / "Downloads").mkdir()
    (user / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "Default").mkdir(
        parents=True,
    )
    (user / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Recent").mkdir(
        parents=True,
    )
    (root / "Windows" / "System32" / "config").mkdir(parents=True)
    (root / "Windows" / "System32" / "winevt" / "Logs").mkdir(parents=True)
    (root / "$Recycle.Bin" / "S-1-5-21-demo").mkdir(parents=True)

    (user / "Documents" / "leak.docx").write_text("sample", encoding="utf-8")
    (user / "Downloads" / "course.zip").write_text("sample", encoding="utf-8")
    (
        user / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "Default"
        / "History"
    ).write_text("sqlite", encoding="utf-8")
    (
        user / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Recent"
        / "leak.lnk"
    ).write_text("shortcut", encoding="utf-8")
    (user / "NTUSER.DAT").write_text("registry", encoding="utf-8")
    (root / "Windows" / "System32" / "config" / "SOFTWARE").write_text(
        "registry",
        encoding="utf-8",
    )
    (root / "Windows" / "System32" / "winevt" / "Logs" / "System.evtx").write_text(
        "evtx",
        encoding="utf-8",
    )
    (root / "$Recycle.Bin" / "S-1-5-21-demo" / "$IABC123").write_text(
        "recycle",
        encoding="utf-8",
    )
    return root
