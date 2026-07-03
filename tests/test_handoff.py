from pathlib import Path

from hzltfw.core.handoff import export_handoff_markdown, render_handoff_markdown


def test_render_handoff_markdown_includes_windows_sources() -> None:
    markdown = render_handoff_markdown(
        case_name="Demo Case",
        operator="tester",
        source_image="sample.E01",
        sample_sha256="abc123",
    )

    assert "Windows Evidence Handoff Checklist" in markdown
    assert "sample.E01" in markdown
    assert "Users\\<user>\\Documents" in markdown
    assert "Windows\\System32\\winevt\\Logs\\*.evtx" in markdown
    assert "hzltfw analyzes exported files and directories" in markdown


def test_export_handoff_markdown(tmp_path: Path) -> None:
    output = export_handoff_markdown(
        tmp_path / "handoff.md",
        case_name="CASE-001",
    )

    assert output.exists()
    assert "CASE-001" in output.read_text(encoding="utf-8")
