from pathlib import Path

# Apply engineio ASGI patch before NiceGUI initializes the Socket.IO app.
# Must run before nicegui imports because NiceGUI creates the Socket.IO app
# at module level.
from hzltfw._engineio_patch import apply as _apply_eio_patch

<<<<<<< Updated upstream
from hzltfw.core.database import create_db_engine, init_db, sqlite_url
from hzltfw.ui.pages.analysis import register_analysis_page
from hzltfw.ui.pages.artifacts import register_artifacts_page
from hzltfw.ui.pages.cases import register_cases_page
from hzltfw.ui.pages.evidence import register_evidence_page
from hzltfw.ui.pages.reports import register_reports_page
=======
_apply_eio_patch()

from nicegui import ui  # noqa: E402

from hzltfw.core.database import create_db_engine, init_db, sqlite_url  # noqa: E402
from hzltfw.ui.pages.analysis import register_analysis_page  # noqa: E402
from hzltfw.ui.pages.artifacts import register_artifacts_page  # noqa: E402
from hzltfw.ui.pages.cases import register_cases_page  # noqa: E402
from hzltfw.ui.pages.evidence import register_evidence_page  # noqa: E402
from hzltfw.ui.pages.reports import register_reports_page  # noqa: E402
from hzltfw.utils.i18n import t  # noqa: E402
>>>>>>> Stashed changes


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
