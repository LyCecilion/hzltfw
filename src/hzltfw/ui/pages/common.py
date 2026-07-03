from nicegui import ui

from hzltfw.utils.i18n import t

APP_SHELL_CSS = """
<style>
  :root {
    --hz-bg: #f5f7fb;
    --hz-surface: #ffffff;
    --hz-border: #d9e2ec;
    --hz-text: #111827;
    --hz-muted: #5b677a;
    --hz-accent: #2563eb;
    --hz-accent-soft: #e8f0ff;
  }

  body {
    background: var(--hz-bg);
    color: var(--hz-text);
  }

  .hz-shell-header {
    background: rgba(255, 255, 255, 0.96) !important;
    color: var(--hz-text) !important;
    border-bottom: 1px solid var(--hz-border);
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
    backdrop-filter: blur(10px);
    min-height: 64px;
  }

  .hz-brand {
    color: var(--hz-text);
    font-weight: 700;
    letter-spacing: 0;
  }

  .hz-nav-link {
    color: #334155 !important;
    text-decoration: none !important;
    padding: 8px 12px;
    border-radius: 8px;
    font-weight: 600;
    line-height: 1;
  }

  .hz-nav-link:hover {
    color: var(--hz-accent) !important;
    background: var(--hz-accent-soft);
  }

  .hz-page {
    padding: 28px 28px 48px;
  }

  .q-card {
    border: 1px solid var(--hz-border);
    border-radius: 8px;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
  }

  .q-field__control {
    min-height: 48px;
  }

  .q-btn {
    border-radius: 7px;
    font-weight: 600;
    text-transform: none;
  }

  .q-table__container {
    border: 1px solid var(--hz-border);
    border-radius: 8px;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04);
  }

  .q-table thead th {
    color: var(--hz-muted);
    font-weight: 700;
    background: #f8fafc;
  }
</style>
"""


def render_nav() -> None:
    ui.add_head_html(APP_SHELL_CSS)
    with ui.header().classes(
        "hz-shell-header items-center justify-between px-6",
    ):
        ui.label(t("app.title")).classes("hz-brand text-lg")
        with ui.row().classes("gap-1 items-center"):
            _nav_link(t("nav.cases"), "/cases")
            _nav_link(t("nav.evidence"), "/evidence")
            _nav_link(t("nav.analysis"), "/analysis")
            _nav_link(t("nav.discoveries"), "/artifacts")
            _nav_link(t("nav.reports"), "/reports")


def page_container():
    return ui.column().classes("hz-page w-full max-w-7xl mx-auto gap-5")


def _nav_link(label: str, target: str) -> None:
    ui.link(label, target).classes("hz-nav-link")
