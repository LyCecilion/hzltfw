from nicegui import ui

from hzltfw.utils.i18n import t


def render_nav() -> None:
    with ui.header().classes("items-center justify-between"):
        ui.label(t("app.title")).classes("text-lg font-semibold")
        with ui.row().classes("gap-2"):
            ui.link(t("nav.cases"), "/cases")
            ui.link(t("nav.evidence"), "/evidence")
            ui.link(t("nav.analysis"), "/analysis")
            ui.link(t("nav.discoveries"), "/artifacts")
            ui.link(t("nav.reports"), "/reports")


def page_container():
    return ui.column().classes("w-full max-w-6xl mx-auto p-4 gap-4")
