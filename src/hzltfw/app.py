from pathlib import Path

from nicegui import ui

from hzltfw.core.database import create_db_engine, init_db, sqlite_url
from hzltfw.ui.pages.analysis import register_analysis_page
from hzltfw.ui.pages.artifacts import register_artifacts_page
from hzltfw.ui.pages.cases import register_cases_page
from hzltfw.ui.pages.evidence import register_evidence_page
from hzltfw.ui.pages.reports import register_reports_page


def run_app(
    *,
    db_path: str | Path = Path(".hzltfw") / "hzltfw.db",
    host: str = "127.0.0.1",
    port: int = 8080,
) -> None:
    engine = create_db_engine(sqlite_url(db_path))
    init_db(engine)

    register_cases_page(engine)
    register_evidence_page(engine)
    register_analysis_page(engine)
    register_artifacts_page(engine)
    register_reports_page(engine)

    ui.run(
        title="Hazelita Forensics Workbench",
        host=host,
        port=port,
        reload=False,
    )
