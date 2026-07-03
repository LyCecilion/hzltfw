from pathlib import Path

from nicegui import ui
from sqlmodel import Session, select

from hzltfw.core.handoff import (
    intake_table_rows,
    missing_table_rows,
    scan_exported_directory,
)
from hzltfw.core.models import Case, EvidenceItem
from hzltfw.core.scanner import scan_evidence
from hzltfw.ui.pages.common import page_container, render_nav
from hzltfw.utils.i18n import t


def register_evidence_page(engine) -> None:
    @ui.page("/evidence")
    def evidence_page() -> None:
        render_nav()
        with page_container():
            ui.label(t("evidence.title")).classes("text-2xl font-semibold")

            with Session(engine) as session:
                cases = list(
                    session.exec(select(Case).order_by(Case.created_at.desc())),
                )
                evidence_rows = list(session.exec(select(EvidenceItem)))

            case_options = {case.id: f"{case.case_no} - {case.name}" for case in cases}
            with ui.card().classes("w-full"):
                ui.label(t("evidence.add")).classes("text-lg font-medium")
                case_select = ui.select(
                    options=case_options,
                    label=t("evidence.case"),
                    value=next(iter(case_options), None),
                ).classes("w-full")
                source_path = ui.input(t("evidence.path")).classes(
                    "w-full",
                )
                name = ui.input(t("evidence.name")).classes("w-full")
                operator = ui.input(t("evidence.operator")).classes("w-full")

                with ui.expansion(t("evidence.intake"), icon="folder_open").classes(
                    "w-full",
                ):
                    found_table = ui.table(
                        columns=[
                            {
                                "name": "category",
                                "label": "Recognized Source",
                                "field": "category",
                            },
                            {"name": "path", "label": "Path", "field": "path"},
                            {"name": "kind", "label": "Kind", "field": "kind"},
                            {"name": "size", "label": "Size", "field": "size"},
                        ],
                        rows=[],
                    ).classes("w-full")
                    missing_table = ui.table(
                        columns=[
                            {
                                "name": "category",
                                "label": "Typical Source Not Found",
                                "field": "category",
                            },
                        ],
                        rows=[],
                    ).classes("w-full")

                    def inspect_windows_export() -> None:
                        path = Path(source_path.value or "").expanduser()
                        if not path.exists() or not path.is_dir():
                            ui.notify(
                                "Enter an exported Windows directory path.",
                                type="warning",
                            )
                            return
                        result = scan_exported_directory(path)
                        found_table.rows = intake_table_rows(result)
                        missing_table.rows = missing_table_rows(result)
                        found_table.update()
                        missing_table.update()
                        ui.notify(
                            f"Found {len(result.findings)} recognizable sources.",
                        )

                    ui.button(t("evidence.check"), on_click=inspect_windows_export)

                def add_evidence() -> None:
                    path = Path(source_path.value or "").expanduser()
                    if not case_select.value:
                        ui.notify(t("notify.create_case_first"), type="warning")
                        return
                    if not path.exists():
                        ui.notify(t("notify.evidence_missing"), type="negative")
                        return
                    evidence_type = "directory" if path.is_dir() else "file"
                    with Session(engine) as session:
                        evidence = EvidenceItem(
                            case_id=case_select.value,
                            name=name.value or path.name,
                            source_path=str(path.resolve()),
                            evidence_type=evidence_type,
                            operator=operator.value or "",
                        )
                        session.add(evidence)
                        session.commit()
                        session.refresh(evidence)
                        scan_evidence(session, evidence)
                    ui.notify(t("notify.evidence_added"))
                    ui.navigate.reload()

                ui.button(t("evidence.add_scan"), on_click=add_evidence)

            ui.table(
                columns=[
                    {"name": "id", "label": "ID", "field": "id"},
                    {"name": "case_id", "label": "Case", "field": "case_id"},
                    {"name": "name", "label": "Name", "field": "name"},
                    {"name": "type", "label": "Type", "field": "type"},
                    {"name": "size", "label": "Size", "field": "size"},
                    {"name": "source", "label": "Source", "field": "source"},
                ],
                rows=[
                    {
                        "id": row.id,
                        "case_id": row.case_id,
                        "name": row.name,
                        "type": row.evidence_type,
                        "size": row.size_bytes,
                        "source": row.source_path,
                    }
                    for row in evidence_rows
                ],
            ).classes("w-full")
