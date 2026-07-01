from pathlib import Path

from sqlmodel import Session, select

from hzltfw import __version__
from hzltfw.core.database import create_db_engine, init_db
from hzltfw.core.models import Artifact, Case, EvidenceFile, EvidenceItem, PluginRun
from hzltfw.core.report import export_case_markdown
from hzltfw.core.runner import run_plugins_for_evidence
from hzltfw.core.scanner import scan_evidence

EXPECTED_FILE_COUNT = 2


def test_import_version() -> None:
    assert __version__


def test_vertical_slice(tmp_path: Path) -> None:
    evidence_dir = tmp_path / "sample_evidence"
    evidence_dir.mkdir()
    (evidence_dir / "notes.txt").write_text("course material leak", encoding="utf-8")
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
        assert len(files) == EXPECTED_FILE_COUNT

        runs = run_plugins_for_evidence(session, evidence.id or 0)
        assert len(runs) == 1
        assert runs[0].status == "success"

        artifact = session.exec(select(Artifact)).one()
        assert artifact.artifact_type == "hash.manifest"
        assert artifact.data_json["file_count"] == EXPECTED_FILE_COUNT

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
