from nicegui import ui
from sqlmodel import Session, select

from hzltfw.core.models import EvidenceFile, EvidenceItem, PluginRun
from hzltfw.core.runner import run_plugins_for_evidence
from hzltfw.core.scanner import scan_evidence
from hzltfw.ui.pages.common import page_container, render_nav


def register_analysis_page(engine) -> None:
    @ui.page("/analysis")
    def analysis_page() -> None:
        render_nav()
        with page_container():
            ui.label("Analysis").classes("text-2xl font-semibold")

            with Session(engine) as session:
                evidence_items = list(session.exec(select(EvidenceItem)))
                runs = list(
                    session.exec(
                        select(PluginRun).order_by(PluginRun.started_at.desc()),
                    ),
                )

            evidence_options = {
                evidence.id: f"{evidence.id} - {evidence.name}"
                for evidence in evidence_items
            }
            with ui.card().classes("w-full"):
                ui.label("Run Plugins").classes("text-lg font-medium")
                evidence_select = ui.select(
                    options=evidence_options,
                    label="Evidence",
                    value=next(iter(evidence_options), None),
                ).classes("w-full")

                def run_analysis() -> None:
                    if not evidence_select.value:
                        ui.notify("Add evidence first.", type="warning")
                        return
                    with Session(engine) as session:
                        evidence = session.get(EvidenceItem, evidence_select.value)
                        if evidence is None:
                            ui.notify("Evidence not found.", type="negative")
                            return
                        file_count = session.exec(
                            select(EvidenceFile).where(
                                EvidenceFile.evidence_id == evidence.id,
                            ),
                        ).first()
                        if file_count is None:
                            scan_evidence(session, evidence)
                        run_plugins_for_evidence(session, evidence.id or 0)
                    ui.notify("Analysis finished.")
                    ui.navigate.reload()

                ui.button("Run Default Plugins", on_click=run_analysis)

            ui.table(
                columns=[
                    {"name": "plugin", "label": "Plugin", "field": "plugin"},
                    {"name": "status", "label": "Status", "field": "status"},
                    {"name": "started", "label": "Started", "field": "started"},
                    {"name": "finished", "label": "Finished", "field": "finished"},
                    {"name": "error", "label": "Error", "field": "error"},
                ],
                rows=[
                    {
                        "plugin": run.plugin_name,
                        "status": run.status,
                        "started": run.started_at.isoformat(),
                        "finished": (
                            run.finished_at.isoformat() if run.finished_at else ""
                        ),
                        "error": run.error_message or "",
                    }
                    for run in runs
                ],
            ).classes("w-full")
