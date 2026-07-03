from pathlib import Path

from nicegui import ui

from hzltfw.core.handoff import export_handoff_markdown, handoff_table_rows
from hzltfw.ui.pages.common import page_container, render_nav


def register_handoff_page() -> None:
    @ui.page("/handoff")
    def handoff_page() -> None:
        render_nav()
        with page_container():
            ui.label("Evidence Handoff").classes("text-2xl font-semibold")

            ui.table(
                columns=[
                    {"name": "category", "label": "Category", "field": "category"},
                    {"name": "paths", "label": "Paths", "field": "paths"},
                    {"name": "purpose", "label": "Purpose", "field": "purpose"},
                    {"name": "plugins", "label": "Plugins", "field": "plugins"},
                ],
                rows=handoff_table_rows(),
            ).classes("w-full")

            with ui.card().classes("w-full"):
                ui.label("Export Checklist").classes("text-lg font-medium")
                case_name = ui.input("Case name").classes("w-full")
                operator = ui.input("Operator").classes("w-full")
                source_image = ui.input("Source image").classes("w-full")
                sample_sha256 = ui.input("Sample SHA256").classes("w-full")
                output_path = ui.input(
                    "Output path",
                    value=str(Path("reports") / "evidence-handoff.md"),
                ).classes("w-full")

                def export_checklist() -> None:
                    path = export_handoff_markdown(
                        output_path.value,
                        case_name=case_name.value or "",
                        operator=operator.value or "",
                        source_image=source_image.value or "",
                        sample_sha256=sample_sha256.value or "",
                    )
                    ui.notify(f"Handoff checklist exported: {path}")

                ui.button("Export Markdown", on_click=export_checklist)
