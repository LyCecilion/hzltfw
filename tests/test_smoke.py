from pathlib import Path

from sqlmodel import Session, select

from hzltfw import __version__
from hzltfw.core.database import create_db_engine, init_db
from hzltfw.core.models import Artifact, Case, EvidenceFile, EvidenceItem, PluginRun
from hzltfw.core.report import export_case_markdown
from hzltfw.core.runner import run_plugins_for_evidence
from hzltfw.core.scanner import scan_evidence

EXPECTED_FILE_COUNT = 2
EXPECTED_DEFAULT_PLUGIN_COUNT = 3


def test_import_version() -> None:
    assert __version__


def test_vertical_slice(tmp_path: Path) -> None:
    evidence_dir = tmp_path / "sample_evidence"
    evidence_dir.mkdir()
    (evidence_dir / "notes.txt").write_text(
        "course material leak\n"
        "contact: demo@example.test\n"
        "phone: 13800138000\n"
        "student id: 25212345678\n",
        encoding="utf-8",
    )
    (evidence_dir / "fake.jpg").write_bytes(b"%PDF-1.7\n% fake pdf")
    (evidence_dir / "nested").mkdir()
    (evidence_dir / "nested" / "readme.txt").write_text("hello", encoding="utf-8")

    engine = create_db_engine(f"sqlite:///{tmp_path / 'test.db'}")
    init_db(engine)

    with Session(engine) as session:
        case = Case(
            case_no="CASE-001",
            name="Smoke Test",
            investigator="tester",
        )
        session.add(case)
        session.commit()
        session.refresh(case)

        evidence = EvidenceItem(
            case_id=case.id or 0,
            name="sample_evidence",
            source_path=str(evidence_dir),
            evidence_type="directory",
        )
        session.add(evidence)
        session.commit()
        session.refresh(evidence)

        files = scan_evidence(session, evidence)
        assert len(files) == EXPECTED_FILE_COUNT + 1

        runs = run_plugins_for_evidence(session, evidence.id or 0)
        assert len(runs) == EXPECTED_DEFAULT_PLUGIN_COUNT
        assert all(run.status == "success" for run in runs)

        artifacts = list(session.exec(select(Artifact)))
        manifest = next(
            artifact
            for artifact in artifacts
            if artifact.artifact_type == "hash.manifest"
        )
        mismatch = next(
            artifact
            for artifact in artifacts
            if artifact.artifact_type == "file.type_mismatch"
        )
        regex_hits = [
            artifact
            for artifact in artifacts
            if artifact.artifact_type == "keyword.regex_hit"
        ]
        assert manifest.data_json["file_count"] == EXPECTED_FILE_COUNT + 1
        assert mismatch.source_path == "fake.jpg"
        assert mismatch.severity == "medium"
        assert {artifact.data_json["rule"] for artifact in regex_hits} == {
            "email",
            "phone_cn",
            "student_id",
        }
        assert all(artifact.is_key for artifact in regex_hits)
        assert all(artifact.severity == "medium" for artifact in regex_hits)

        assert session.exec(select(EvidenceFile)).first() is not None
        assert session.exec(select(PluginRun)).first() is not None

        report_path = export_case_markdown(
            session,
            case.id or 0,
            tmp_path / "report.md",
            include_manifest=True,
        )

    report = report_path.read_text(encoding="utf-8")
    assert "Electronic Data Forensics Analysis Report" in report
    assert "hash_manifest" in report
    assert "file_type" in report
    assert "keyword_search" in report
