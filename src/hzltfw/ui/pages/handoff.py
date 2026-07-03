from pathlib import Path

from nicegui import ui

from hzltfw.core.handoff import (
    export_handoff_markdown,
    handoff_table_rows,
    intake_table_rows,
    missing_table_rows,
    scan_exported_directory,
)
from hzltfw.ui.pages.common import page_container, render_nav


def register_handoff_page() -> None:
    @ui.page("/handoff")
    def handoff_page() -> None:
        render_nav()
        with page_container():
            ui.label("Evidence Intake").classes("text-2xl font-semibold")

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
                ui.label("Inspect Exported Directory").classes("text-lg font-medium")
                exported_root = ui.input("Exported directory path").classes("w-full")

                found_table = ui.table(
                    columns=[
                        {"name": "category", "label": "Category", "field": "category"},
                        {"name": "path", "label": "Path", "field": "path"},
                        {"name": "kind", "label": "Kind", "field": "kind"},
                        {"name": "size", "label": "Size", "field": "size"},
                    ],
                    rows=[],
                ).classes("w-full")
                missing_table = ui.table(
                    columns=[
                        {"name": "category", "label": "Missing", "field": "category"},
                    ],
                    rows=[],
                ).classes("w-full")

                def inspect_export() -> None:
                    if not exported_root.value:
                        ui.notify("Enter an exported directory path.", type="warning")
                        return
                    try:
                        result = scan_exported_directory(exported_root.value)
                    except NotADirectoryError:
                        ui.notify("Exported directory does not exist.", type="negative")
                        return

                    found_table.rows = intake_table_rows(result)
                    missing_table.rows = missing_table_rows(result)
                    found_table.update()
                    missing_table.update()
                    ui.notify(f"Found {len(result.findings)} candidate sources.")

                ui.button("Inspect Directory", on_click=inspect_export)

            with ui.card().classes("w-full"):
                ui.label("Export Intake Report").classes("text-lg font-medium")
                case_name = ui.input("Case name").classes("w-full")
                operator = ui.input("Operator").classes("w-full")
                source_image = ui.input("Source image").classes("w-full")
                sample_sha256 = ui.input("Sample SHA256").classes("w-full")
                output_path = ui.input(
                    "Output path",
                    value=str(Path("reports") / "evidence-handoff.md"),
                ).classes("w-full")

                def export_checklist() -> None:
                    try:
                        path = export_handoff_markdown(
                            output_path.value,
                            case_name=case_name.value or "",
                            operator=operator.value or "",
                            source_image=source_image.value or "",
                            sample_sha256=sample_sha256.value or "",
                            exported_root=exported_root.value or None,
                        )
                    except NotADirectoryError:
                        ui.notify(
                            "Exported directory does not exist.",
                            type="negative",
                        )
                        return
                    ui.notify(f"Intake report exported: {path}")

                ui.button("Export Markdown", on_click=export_checklist)
