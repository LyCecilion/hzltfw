from pathlib import Path
from zipfile import ZipFile

from docx import Document
from PIL import Image
from pypdf import PdfWriter
from sqlmodel import Session, select

from hzltfw import __version__
from hzltfw.core.database import create_db_engine, init_db
from hzltfw.core.models import Artifact, Case, EvidenceFile, EvidenceItem, PluginRun
from hzltfw.core.records import delete_case_record, delete_evidence_record
from hzltfw.core.report import export_case_markdown
from hzltfw.core.runner import run_plugins_for_evidence
from hzltfw.core.scanner import scan_evidence

EXPECTED_FILE_COUNT = 7
EXPECTED_DEFAULT_PLUGIN_COUNT = 5
EXPECTED_ARCHIVE_ENTRY_COUNT = 2
EXPECTED_SUSPICIOUS_ARCHIVE_ENTRY_COUNT = 1
EXIF_MAKE = 271
EXIF_MODEL = 272
EXIF_DATETIME_ORIGINAL = 36867


def test_import_version() -> None:
    assert __version__


def test_vertical_slice(tmp_path: Path) -> None:
    evidence_dir = tmp_path / "sample_evidence"
    _write_sample_evidence(evidence_dir)

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
        assert len(runs) == EXPECTED_DEFAULT_PLUGIN_COUNT
        assert all(run.status == "success" for run in runs)

        artifacts = list(session.exec(select(Artifact)))
        _assert_artifacts(artifacts)

        assert session.exec(select(EvidenceFile)).first() is not None
        assert session.exec(select(PluginRun)).first() is not None

        report_path = export_case_markdown(
            session,
            case.id or 0,
            tmp_path / "report.md",
            include_manifest=True,
        )

    report = report_path.read_text(encoding="utf-8")
    assert "电子数据取证分析报告" in report
    assert "hash_manifest" in report
    assert "file_type" in report
    assert "keyword_search" in report
    assert "archive_index" in report
    assert "metadata_extract" in report


def test_delete_evidence_record_removes_related_rows(tmp_path: Path) -> None:
    engine = create_db_engine(f"sqlite:///{tmp_path / 'delete-evidence.db'}")
    init_db(engine)

    with Session(engine) as session:
        case = Case(case_no="CASE-DEL-E", name="Delete Evidence")
        session.add(case)
        session.commit()
        session.refresh(case)

        evidence = EvidenceItem(
            case_id=case.id or 0,
            name="USB image",
            source_path=str(tmp_path),
            evidence_type="directory",
        )
        session.add(evidence)
        session.commit()
        session.refresh(evidence)

        run = PluginRun(
            case_id=case.id or 0,
            evidence_id=evidence.id,
            plugin_name="sample",
            plugin_version="1.0",
            status="success",
        )
        session.add(run)
        session.commit()
        session.refresh(run)

        session.add(
            EvidenceFile(
                evidence_id=evidence.id or 0,
                relative_path="a.txt",
                virtual_path="USB image/a.txt",
            )
        )
        session.add(
            Artifact(
                case_id=case.id or 0,
                evidence_id=evidence.id,
                plugin_run_id=run.id or 0,
                artifact_type="sample",
                title="Sample Artifact",
            )
        )
        session.commit()

        assert delete_evidence_record(session, evidence.id or 0)
        assert session.get(EvidenceItem, evidence.id) is None
        assert session.exec(select(EvidenceFile)).first() is None
        assert session.exec(select(PluginRun)).first() is None
        assert session.exec(select(Artifact)).first() is None
        assert session.get(Case, case.id) is not None


def test_delete_case_record_removes_related_rows(tmp_path: Path) -> None:
    engine = create_db_engine(f"sqlite:///{tmp_path / 'delete-case.db'}")
    init_db(engine)

    with Session(engine) as session:
        case = Case(case_no="CASE-DEL-C", name="Delete Case")
        session.add(case)
        session.commit()
        session.refresh(case)

        evidence = EvidenceItem(
            case_id=case.id or 0,
            name="Laptop export",
            source_path=str(tmp_path),
            evidence_type="directory",
        )
        session.add(evidence)
        session.commit()
        session.refresh(evidence)

        run = PluginRun(
            case_id=case.id or 0,
            evidence_id=evidence.id,
            plugin_name="sample",
            plugin_version="1.0",
            status="success",
        )
        session.add(run)
        session.commit()
        session.refresh(run)

        session.add(
            EvidenceFile(
                evidence_id=evidence.id or 0,
                relative_path="a.txt",
                virtual_path="Laptop export/a.txt",
            )
        )
        session.add(
            Artifact(
                case_id=case.id or 0,
                evidence_id=evidence.id,
                plugin_run_id=run.id or 0,
                artifact_type="sample",
                title="Sample Artifact",
            )
        )
        session.commit()

        assert delete_case_record(session, case.id or 0)
        assert session.get(Case, case.id) is None
        assert session.exec(select(EvidenceItem)).first() is None
        assert session.exec(select(EvidenceFile)).first() is None
        assert session.exec(select(PluginRun)).first() is None
        assert session.exec(select(Artifact)).first() is None


def _write_sample_evidence(evidence_dir: Path) -> None:
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
    _write_image_sample(evidence_dir / "photo.jpg")
    _write_pdf_sample(evidence_dir / "memo.pdf")
    _write_docx_sample(evidence_dir / "handoff.docx")
    with ZipFile(evidence_dir / "downloads.zip", "w") as archive:
        archive.writestr("课程资料/25212345678_roster.txt", "sample")
        archive.writestr("normal/readme.txt", "hello")


def _write_image_sample(path: Path) -> None:
    image = Image.new("RGB", (16, 16), color="white")
    exif = Image.Exif()
    exif[EXIF_MAKE] = "Hazelita"
    exif[EXIF_MODEL] = "DemoCam"
    exif[EXIF_DATETIME_ORIGINAL] = "2026:07:03 10:11:12"
    image.save(path, exif=exif)


def _write_pdf_sample(path: Path) -> None:
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    writer.add_metadata(
        {
            "/Title": "Course Leak Report",
            "/Author": "Demo Investigator",
            "/CreationDate": "D:20260703101112Z",
        },
    )
    with path.open("wb") as file:
        writer.write(file)


def _write_docx_sample(path: Path) -> None:
    document = Document()
    document.add_paragraph("Course handoff notes")
    document.core_properties.title = "Course Handoff"
    document.core_properties.author = "Demo Investigator"
    document.save(path)


def _assert_artifacts(artifacts: list[Artifact]) -> None:
    manifest = _artifact(artifacts, "hash.manifest")
    mismatch = _artifact(artifacts, "file.type_mismatch")
    archive_index = _artifact(artifacts, "archive.index")
    archive_entry = _artifact(artifacts, "archive.entry")

    assert manifest.data_json["file_count"] == EXPECTED_FILE_COUNT
    assert mismatch.source_path == "fake.jpg"
    assert mismatch.severity == "medium"
    assert not [
        artifact for artifact in artifacts if artifact.artifact_type == "file.type"
    ]
    assert archive_index.data_json["entry_count"] == EXPECTED_ARCHIVE_ENTRY_COUNT
    assert (
        archive_index.data_json["suspicious_entry_count"]
        == EXPECTED_SUSPICIOUS_ARCHIVE_ENTRY_COUNT
    )
    assert archive_entry.is_key
    assert archive_entry.source_path == (
        "downloads.zip!/课程资料/25212345678_roster.txt"
    )
    _assert_regex_hits(artifacts)
    _assert_metadata_artifacts(artifacts)


def _assert_regex_hits(artifacts: list[Artifact]) -> None:
    regex_hits = [
        artifact
        for artifact in artifacts
        if artifact.artifact_type == "keyword.regex_hit"
    ]
    assert {artifact.data_json["rule"] for artifact in regex_hits} == {
        "email",
        "phone_cn",
        "student_id",
    }
    assert all(artifact.is_key for artifact in regex_hits)
    assert all(artifact.severity == "medium" for artifact in regex_hits)


def _assert_metadata_artifacts(artifacts: list[Artifact]) -> None:
    image_metadata = _artifact(artifacts, "metadata.image")
    pdf_metadata = _artifact(artifacts, "metadata.pdf")
    office_metadata = _artifact(artifacts, "metadata.office")

    assert image_metadata.data_json["exif"]["Make"] == "Hazelita"
    assert pdf_metadata.data_json["metadata"]["Title"] == "Course Leak Report"
    assert pdf_metadata.data_json["page_count"] == 1
    assert office_metadata.data_json["metadata"]["author"] == "Demo Investigator"


def _artifact(artifacts: list[Artifact], artifact_type: str) -> Artifact:
    return next(
        artifact for artifact in artifacts if artifact.artifact_type == artifact_type
    )
