from nicegui import ui


def render_nav() -> None:
    with ui.header().classes("items-center justify-between"):
        ui.label("Hazelita Forensics Workbench").classes("text-lg font-semibold")
        with ui.row().classes("gap-2"):
            ui.link("Cases", "/cases")
            ui.link("Evidence", "/evidence")
            ui.link("Handoff", "/handoff")
            ui.link("Analysis", "/analysis")
            ui.link("Artifacts", "/artifacts")
            ui.link("Reports", "/reports")


def page_container():
    return ui.column().classes("w-full max-w-6xl mx-auto p-4 gap-4")
