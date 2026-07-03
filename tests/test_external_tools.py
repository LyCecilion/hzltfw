import sys
import tarfile
from pathlib import Path
from zipfile import ZipFile

from sqlmodel import Session, select

from hzltfw.core.config import (
    AppConfig,
    ExternalToolConfig,
    default_config,
    load_config,
    save_config,
)
from hzltfw.core.database import create_db_engine, init_db
from hzltfw.core.external_probe import probe_external_input
from hzltfw.core.external_tools import check_tool_health, run_external_tool
from hzltfw.core.models import Artifact, Case, EvidenceItem
from hzltfw.core.report import export_case_report_bundle
from hzltfw.core.runner import run_plugins_for_evidence
from hzltfw.core.scanner import scan_evidence
from hzltfw.plugins.external_forensics import ExternalForensicsPlugin


def test_config_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    config = AppConfig(
        language="en-US",
        external_tools={
            "demo": ExternalToolConfig(
                name="demo",
                command=["python", "demo.py"],
                enabled=False,
            ),
        },
    )

    save_config(config, path)
    loaded = load_config(path)

    assert loaded.language == "en-US"
    assert loaded.external_tools["demo"].command == ["python", "demo.py"]
    assert not loaded.external_tools["demo"].enabled


def test_default_config_uses_chinese_language() -> None:
    assert default_config().language == "zh-CN"


def test_external_tool_health_and_run(tmp_path: Path) -> None:
    script = _write_fake_tool(tmp_path)
    command = [sys.executable, str(script)]
    tool = ExternalToolConfig(name="fake", command=command)

    health = check_tool_health(tool)
    assert health.available

    output_dir = tmp_path / "run"
    result = run_external_tool(
        tool_name="fake",
        command_prefix=command,
        arguments=["-o", str(output_dir)],
        output_dir=output_dir,
    )

    assert result.success
    assert "fake output" in result.stdout
    assert (output_dir / "index.html").exists()


def test_external_tool_health_reports_missing_command() -> None:
    health = check_tool_health(
        ExternalToolConfig(name="missing", command=["not-a-real-hzltfw-tool"]),
    )

    assert not health.available
    assert "Executable not found" in health.message


def test_probe_android_directory(tmp_path: Path) -> None:
    root = tmp_path / "android"
    (root / "data" / "data" / "com.android.chrome").mkdir(parents=True)

    result = probe_external_input(root)

    assert result.input_type == "fs"
    assert result.suggestions[0].tool_name == "aleapp"


def test_probe_ios_zip(tmp_path: Path) -> None:
    archive_path = tmp_path / "ios.zip"
    with ZipFile(archive_path, "w") as archive:
        archive.writestr("Manifest.db", "sqlite")
        archive.writestr("HomeDomain/Library/Preferences/demo.plist", "plist")

    result = probe_external_input(archive_path)

    assert result.input_type == "zip"
    assert result.suggestions[0].tool_name == "ileapp"


def test_probe_chromium_tar(tmp_path: Path) -> None:
    source = tmp_path / "profile"
    (source / "Default").mkdir(parents=True)
    (source / "Default" / "History").write_text("sqlite", encoding="utf-8")
    archive_path = tmp_path / "profile.tar"
    with tarfile.open(archive_path, "w") as archive:
        archive.add(source, arcname="Chrome")

    result = probe_external_input(archive_path)

    assert result.input_type == "tar"
    assert result.suggestions[0].tool_name == "hindsight"


def test_external_forensics_plugin_creates_report_artifact(tmp_path: Path) -> None:
    evidence_dir = tmp_path / "android"
    (evidence_dir / "data" / "data" / "com.android.chrome").mkdir(parents=True)
    (evidence_dir / "data" / "data" / "com.android.chrome" / "prefs.xml").write_text(
        "demo",
        encoding="utf-8",
    )
    tool = ExternalToolConfig(
        name="aleapp",
        command=[sys.executable, str(_write_fake_tool(tmp_path))],
    )
    engine = create_db_engine(f"sqlite:///{tmp_path / 'test.db'}")
    init_db(engine)

    with Session(engine) as session:
        case = Case(case_no="CASE-EXT", name="External Test")
        session.add(case)
        session.commit()
        session.refresh(case)
        evidence = EvidenceItem(
            case_id=case.id or 0,
            name="android",
            source_path=str(evidence_dir),
            evidence_type="directory",
        )
        session.add(evidence)
        session.commit()
        session.refresh(evidence)
        scan_evidence(session, evidence)

        runs = run_plugins_for_evidence(
            session,
            evidence.id or 0,
            plugins=[
                ExternalForensicsPlugin(
                    "aleapp",
                    input_type="fs",
                    tool_config=tool,
                ),
            ],
        )
        artifacts = list(session.exec(select(Artifact)))

    assert runs[0].status == "success"
    assert artifacts[0].artifact_type == "external.report"
    assert artifacts[0].data_json["tool_name"] == "aleapp"
    assert Path(artifacts[0].data_json["report_path"]).name == "index.html"


def test_report_bundle_copies_external_outputs(tmp_path: Path) -> None:
    evidence_dir = tmp_path / "android"
    (evidence_dir / "data" / "data" / "com.android.chrome").mkdir(parents=True)
    tool = ExternalToolConfig(
        name="aleapp",
        command=[sys.executable, str(_write_fake_tool(tmp_path))],
    )
    engine = create_db_engine(f"sqlite:///{tmp_path / 'bundle.db'}")
    init_db(engine)

    with Session(engine) as session:
        case = Case(case_no="CASE-BUNDLE", name="Bundle Test")
        session.add(case)
        session.commit()
        session.refresh(case)
        evidence = EvidenceItem(
            case_id=case.id or 0,
            name="android",
            source_path=str(evidence_dir),
            evidence_type="directory",
        )
        session.add(evidence)
        session.commit()
        session.refresh(evidence)
        scan_evidence(session, evidence)
        run_plugins_for_evidence(
            session,
            evidence.id or 0,
            plugins=[
                ExternalForensicsPlugin(
                    "aleapp",
                    input_type="fs",
                    tool_config=tool,
                ),
            ],
        )

        report_path = export_case_report_bundle(
            session,
            case.id or 0,
            tmp_path / "bundle",
        )

    report = report_path.read_text(encoding="utf-8")
    assert "外部工具报告" in report
    assert "external/aleapp/run-" in report
    assert next((tmp_path / "bundle" / "external").rglob("index.html")).exists()


def _write_fake_tool(tmp_path: Path) -> Path:
    script = tmp_path / "fake_tool.py"
    script.write_text(
        "import pathlib, sys\n"
        "if '--help' in sys.argv:\n"
        "    print('fake help')\n"
        "    raise SystemExit(0)\n"
        "output = pathlib.Path.cwd()\n"
        "for flag in ('-o', '--output_path'):\n"
        "    if flag in sys.argv:\n"
        "        output = pathlib.Path(sys.argv[sys.argv.index(flag) + 1])\n"
        "if not output.exists():\n"
        "    print('OUTPUT folder does not exist!', file=sys.stderr)\n"
        "    raise SystemExit(2)\n"
        "(output / 'index.html').write_text('<html>ok</html>')\n"
        "print('fake output')\n",
        encoding="utf-8",
    )
    return script
