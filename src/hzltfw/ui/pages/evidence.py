from pathlib import Path

from nicegui import ui
from sqlmodel import Session, select

from hzltfw.core.models import Case, EvidenceItem
from hzltfw.core.scanner import scan_evidence
from hzltfw.ui.pages.common import page_container, render_nav


def register_evidence_page(engine) -> None:
    @ui.page("/evidence")
    def evidence_page() -> None:
        render_nav()
        with page_container():
            ui.label("Evidence").classes("text-2xl font-semibold")

            with Session(engine) as session:
                cases = list(
                    session.exec(select(Case).order_by(Case.created_at.desc())),
                )
                evidence_rows = list(session.exec(select(EvidenceItem)))

            case_options = {case.id: f"{case.case_no} - {case.name}" for case in cases}
            with ui.card().classes("w-full"):
                ui.label("Add Evidence").classes("text-lg font-medium")
                case_select = ui.select(
                    options=case_options,
                    label="Case",
                    value=next(iter(case_options), None),
                ).classes("w-full")
                source_path = ui.input("Evidence file or directory path").classes(
                    "w-full",
                )
                name = ui.input("Evidence name").classes("w-full")
                operator = ui.input("Operator").classes("w-full")

                def add_evidence() -> None:
                    path = Path(source_path.value or "").expanduser()
                    if not case_select.value:
                        ui.notify("Create a case first.", type="warning")
                        return
                    if not path.exists():
                        ui.notify("Evidence path does not exist.", type="negative")
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
                    ui.notify("Evidence added and scanned.")
                    ui.navigate.reload()

                ui.button("Add and Scan", on_click=add_evidence)

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
