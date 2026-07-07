from pathlib import Path

from hzltfw._engineio_patch import apply_engineio_asgi_disconnect_patch
from hzltfw.core.database import create_db_engine, init_db, sqlite_url

apply_engineio_asgi_disconnect_patch()

from nicegui import ui  # noqa: E402

from hzltfw.ui.pages.analysis import register_analysis_page  # noqa: E402
from hzltfw.ui.pages.artifacts import register_artifacts_page  # noqa: E402
from hzltfw.ui.pages.cases import register_cases_page  # noqa: E402
from hzltfw.ui.pages.evidence import register_evidence_page  # noqa: E402
from hzltfw.ui.pages.reports import register_reports_page  # noqa: E402
from hzltfw.utils.i18n import t  # noqa: E402


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
        title=t("app.title"),
        host=host,
        port=port,
        reload=False,
    )
