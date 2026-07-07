from __future__ import annotations

from nicegui import ui

from hzltfw.utils.i18n import t

# ── Workflow Step Definitions ───────────────────────────────────
# Each step maps to a page route and has a label key + description key
# for the sidebar navigation.

STEPS = [
    {"key": "cases", "route": "/cases"},
    {"key": "evidence", "route": "/evidence"},
    {"key": "analysis", "route": "/analysis"},
    {"key": "artifacts", "route": "/artifacts"},
    {"key": "reports", "route": "/reports"},
]

_STEP_LABEL = {
    "cases": "nav.cases",
    "evidence": "nav.evidence",
    "analysis": "nav.analysis",
    "artifacts": "nav.discoveries",
    "reports": "nav.reports",
}

_STEP_DESC = {
    "cases": "sidebar.cases_desc",
    "evidence": "sidebar.evidence_desc",
    "analysis": "sidebar.analysis_desc",
    "artifacts": "sidebar.artifacts_desc",
    "reports": "sidebar.reports_desc",
}

# ── Global CSS ──────────────────────────────────────────────────

APP_SHELL_CSS = """
<style>
  :root {
    --hz-bg: #f1f5f9;
    --hz-surface: #ffffff;
    --hz-border: #e2e8f0;
    --hz-text: #0f172a;
    --hz-text-secondary: #334155;
    --hz-muted: #64748b;
    --hz-muted-light: #94a3b8;
    --hz-accent: #2563eb;
    --hz-accent-hover: #1d4ed8;
    --hz-accent-soft: #eff6ff;
    --hz-sidebar-bg: #0f172a;
    --hz-sidebar-width: 260px;
    --hz-page-header-height: 64px;
    --hz-radius: 10px;
    --hz-radius-sm: 8px;
    --hz-shadow-sm: 0 1px 3px rgba(15, 23, 42, 0.04);
    --hz-shadow-md: 0 4px 12px rgba(15, 23, 42, 0.06);
  }

  body {
    background: var(--hz-bg);
    color: var(--hz-text);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
      'Helvetica Neue', Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  /* ── NiceGUI content override ── */
  .nicegui-content {
    padding: 0 !important;
  }

  /* ── Sidebar ── */
  .hz-sidebar {
    background: linear-gradient(180deg, #0f172a 0%, #1a2740 100%) !important;
    color: #cbd5e1 !important;
    width: var(--hz-sidebar-width) !important;
    border-right: none !important;
    box-shadow: 2px 0 24px rgba(15, 23, 42, 0.3);
    z-index: 1000;
  }

  .hz-sidebar-brand {
    padding: 28px 24px 20px;
  }

  .hz-brand-icon {
    width: 44px;
    height: 44px;
    border-radius: var(--hz-radius);
    background: linear-gradient(135deg, var(--hz-accent), #7c3aed);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35);
    flex-shrink: 0;
  }

  .hz-brand-name {
    font-size: 1.1rem;
    font-weight: 700;
    color: #f1f5f9;
    line-height: 1.2;
    letter-spacing: -0.01em;
  }

  .hz-brand-sub {
    font-size: 0.68rem;
    color: #64748b;
    font-weight: 500;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    line-height: 1.2;
  }

  .hz-sidebar-sep {
    height: 1px;
    background: linear-gradient(
      90deg,
      rgba(148, 163, 184, 0.15) 0%,
      rgba(148, 163, 184, 0.05) 100%
    );
    margin: 0 24px;
  }

  .hz-sidebar-steps {
    padding: 16px 12px;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .hz-sidebar-section-label {
    padding: 4px 12px 10px;
    font-size: 0.65rem;
    font-weight: 700;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.1em;
  }

  /* ── Step Items ── */
  .hz-step {
    display: flex !important;
    align-items: flex-start;
    gap: 12px;
    padding: 10px 12px;
    border-radius: var(--hz-radius-sm);
    color: #94a3b8 !important;
    text-decoration: none !important;
    transition: all 0.18s ease;
    cursor: pointer;
    position: relative;
  }

  .hz-step:hover {
    background: rgba(148, 163, 184, 0.06);
    color: #cbd5e1 !important;
  }

  .hz-step--active {
    background: rgba(37, 99, 235, 0.12) !important;
    color: #f1f5f9 !important;
  }

  .hz-step--active::before {
    content: '';
    position: absolute;
    left: 0;
    top: 8px;
    bottom: 8px;
    width: 3px;
    border-radius: 0 3px 3px 0;
    background: var(--hz-accent);
  }

  .hz-step-num {
    width: 28px;
    height: 28px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.72rem;
    font-weight: 700;
    background: rgba(148, 163, 184, 0.1);
    color: #94a3b8;
    flex-shrink: 0;
    transition: all 0.18s ease;
    line-height: 1;
  }

  .hz-step--active .hz-step-num {
    background: var(--hz-accent);
    color: #fff;
    box-shadow: 0 2px 8px rgba(37, 99, 235, 0.4);
  }

  .hz-step-body {
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-width: 0;
  }

  .hz-step-label {
    font-size: 0.85rem;
    font-weight: 600;
    line-height: 1.3;
    color: inherit;
  }

  .hz-step-desc {
    font-size: 0.7rem;
    color: #64748b;
    line-height: 1.3;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .hz-step--active .hz-step-desc {
    color: #94a3b8;
  }

  /* ── Sidebar Footer ── */
  .hz-sidebar-footer {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 14px 24px;
    border-top: 1px solid rgba(148, 163, 184, 0.08);
    font-size: 0.68rem;
    color: #475569;
    font-weight: 500;
  }

  /* ── Page Header ── */
  .hz-page-header {
    background: #fff;
    border-bottom: 1px solid var(--hz-border);
    padding: 0 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    min-height: var(--hz-page-header-height);
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03);
    position: sticky;
    top: 0;
    z-index: 100;
  }

  .hz-page-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--hz-text);
    letter-spacing: -0.01em;
  }

  .hz-page-subtitle {
    font-size: 0.8rem;
    color: var(--hz-muted);
    font-weight: 400;
  }

  .hz-step-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    background: var(--hz-accent-soft);
    color: var(--hz-accent);
  }

  /* ── Page Content ── */
  .hz-page-content {
    padding: 28px 32px 48px;
    max-width: 1200px;
  }

  /* ── Cards ── */
  .q-card {
    border: 1px solid var(--hz-border) !important;
    border-radius: var(--hz-radius) !important;
    box-shadow: var(--hz-shadow-sm) !important;
    transition: box-shadow 0.2s ease !important;
    background: #fff !important;
  }

  .q-card > .q-card__section {
    padding: 20px 24px !important;
  }

  /* ── Form Fields ── */
  .q-field__control {
    min-height: 44px !important;
    border-radius: var(--hz-radius-sm) !important;
  }

  .q-field--outlined .q-field__control {
    border-radius: var(--hz-radius-sm) !important;
  }

  .q-field__label {
    font-size: 0.85rem !important;
  }

  /* ── Buttons ── */
  .q-btn {
    border-radius: var(--hz-radius-sm) !important;
    font-weight: 600 !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
    padding: 8px 20px !important;
    min-height: 40px !important;
  }

  .q-btn.bg-primary {
    background: var(--hz-accent) !important;
  }

  .q-btn.bg-primary:hover {
    background: var(--hz-accent-hover) !important;
  }

  /* ── Tables ── */
  .q-table__container {
    border: 1px solid var(--hz-border) !important;
    border-radius: var(--hz-radius) !important;
    box-shadow: var(--hz-shadow-sm) !important;
    overflow: hidden !important;
    background: #fff !important;
  }

  .q-table thead th {
    color: var(--hz-muted) !important;
    font-weight: 600 !important;
    background: #f8fafc !important;
    font-size: 0.72rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    padding: 10px 16px !important;
    border-bottom: 2px solid var(--hz-border) !important;
  }

  .q-table tbody td {
    padding: 10px 16px !important;
    font-size: 0.85rem !important;
    border-bottom: 1px solid #f1f5f9 !important;
  }

  .q-table tbody tr:hover td {
    background: #f8fafc !important;
  }

  .q-table tbody tr:last-child td {
    border-bottom: none !important;
  }

  /* ── Expansion panels ── */
  .q-expansion-item {
    border: 1px solid var(--hz-border) !important;
    border-radius: var(--hz-radius-sm) !important;
    overflow: hidden !important;
    margin-top: 8px !important;
  }

  /* ── Select dropdown ── */
  .q-select__dropdown {
    border-radius: var(--hz-radius-sm) !important;
    border: 1px solid var(--hz-border) !important;
    box-shadow: var(--hz-shadow-md) !important;
  }

  /* ── Empty state ── */
  .hz-empty-state {
    text-align: center;
    padding: 48px 24px;
    color: var(--hz-muted);
  }

  .hz-empty-state .material-icons {
    font-size: 3rem;
    color: var(--hz-muted-light);
    margin-bottom: 12px;
  }

  /* ── Stat cards (used on pages that benefit) ── */
  .hz-stat-row {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
  }

  .hz-stat-card {
    background: #fff;
    border: 1px solid var(--hz-border);
    border-radius: var(--hz-radius);
    padding: 18px 22px;
    display: flex;
    align-items: center;
    gap: 14px;
    flex: 1;
    min-width: 160px;
    box-shadow: var(--hz-shadow-sm);
  }

  .hz-stat-icon {
    width: 44px;
    height: 44px;
    border-radius: var(--hz-radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
    flex-shrink: 0;
  }

  .hz-stat-icon--blue   { background: #eff6ff; color: #2563eb; }
  .hz-stat-icon--red    { background: #fef2f2; color: #dc2626; }
  .hz-stat-icon--amber  { background: #fffbeb; color: #d97706; }
  .hz-stat-icon--green  { background: #f0fdf4; color: #16a34a; }

  .hz-stat-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--hz-text);
    line-height: 1.2;
  }

  .hz-stat-label {
    font-size: 0.72rem;
    color: var(--hz-muted);
    font-weight: 500;
  }

  /* ── Section Divider ── */
  .hz-section-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--hz-text);
    margin: 8px 0 12px;
    padding-bottom: 10px;
    border-bottom: 2px solid var(--hz-border);
    display: flex;
    align-items: center;
    gap: 8px;
  }

  /* ── Responsive ── */
  @media (max-width: 768px) {
    .hz-sidebar {
      width: 100% !important;
    }
    .hz-page-header {
      padding: 0 16px;
    }
    .hz-page-content {
      padding: 20px 16px 32px;
    }
    .hz-stat-card {
      flex: 1 1 100%;
    }
  }
</style>
"""


# ── Public API ──────────────────────────────────────────────────


def render_shell(active_key: str) -> None:
    """Render the app shell: left sidebar + page layout.

    Must be called at the top of every page function.  Injects global
    CSS, renders the sidebar with workflow step navigation, and sets
    up the main content area.

    Args:
        active_key: One of ``cases``, ``evidence``, ``analysis``,
            ``artifacts``, ``reports`` — determines which sidebar
            step is highlighted.
    """
    ui.add_head_html(APP_SHELL_CSS)

    active_idx = _step_index(active_key)

    # ── Left Sidebar ──
    with (
        ui.left_drawer(value=True, fixed=True, bordered=False)
        .classes("hz-sidebar")
        .props('behavior="desktop"')
    ):
        _sidebar_brand()
        ui.element("div").classes("hz-sidebar-sep")
        _sidebar_steps(active_idx)
        _sidebar_footer()


def page_header(title: str, *, step: int = 0, total: int = 5) -> None:
    """Render the page header bar with title and step indicator.

    Args:
        title: Page title text.
        step: Current workflow step number (1-based).  0 hides the badge.
        total: Total workflow steps.
    """
    with ui.element("div").classes("hz-page-header"):
        ui.label(title).classes("hz-page-title")
        if step > 0:
            ui.label(f"{t('nav.workflow')}  {step} / {total}").classes("hz-step-badge")


def page_container():
    """Return a context manager for the main page content area.

    Usage::

        with page_container():
            ui.label("Hello")
    """
    return ui.element("div").classes("hz-page-content")


def confirm_action(
    *,
    title: str,
    message: str,
    confirm_label: str,
    on_confirm,
) -> None:
    """Show a small confirmation dialog before running a UI action."""
    with ui.dialog() as dialog, ui.card().classes("min-w-80"):
        ui.label(title).classes("text-lg font-semibold")
        ui.label(message).classes("text-sm text-gray-600")
        with ui.row().classes("w-full justify-end gap-2 mt-4"):
            ui.button(t("common.cancel"), on_click=dialog.close).props("flat")

            def confirm() -> None:
                dialog.close()
                on_confirm()

            ui.button(confirm_label, on_click=confirm, color="negative")

    dialog.open()


# ── Sidebar Internals ───────────────────────────────────────────


def _sidebar_brand() -> None:
    with ui.element("div").classes("hz-sidebar-brand"):  # noqa: SIM117
        with ui.row().classes("items-center gap-3"):
            ui.label("🕵️").classes("hz-brand-icon")
            with ui.column().classes("gap-0"):
                ui.label(t("app.title")).classes("hz-brand-name")
                ui.label(t("app.subtitle").upper()).classes("hz-brand-sub")


def _sidebar_steps(active_idx: int) -> None:
    with ui.element("div").classes("hz-sidebar-steps"):
        ui.label(t("nav.workflow")).classes("hz-sidebar-section-label")
        for i, step in enumerate(STEPS):
            key = step["key"]
            active = i == active_idx
            route = step["route"]

            with ui.link(target=route).classes(
                f"hz-step{' hz-step--active' if active else ''}"
            ):
                ui.label(str(i + 1)).classes("hz-step-num")
                with ui.element("span").classes("hz-step-body"):
                    ui.label(t(_STEP_LABEL[key])).classes("hz-step-label")
                    ui.label(t(_STEP_DESC[key])).classes("hz-step-desc")


def _sidebar_footer() -> None:
    with ui.element("div").classes("hz-sidebar-footer"):
        ui.label("hzltfw  v1.1.0")


# ── Helpers ─────────────────────────────────────────────────────


def _step_index(key: str) -> int:
    for i, step in enumerate(STEPS):
        if step["key"] == key:
            return i
    return 0
