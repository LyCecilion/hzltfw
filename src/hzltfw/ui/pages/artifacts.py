from nicegui import ui
from sqlmodel import Session, select

from hzltfw.core.models import Artifact
from hzltfw.ui.pages.common import page_container, render_nav


def register_artifacts_page(engine) -> None:
    @ui.page("/artifacts")
    def artifacts_page() -> None:
        render_nav()
        with page_container():
            ui.label("Artifacts").classes("text-2xl font-semibold")

            with Session(engine) as session:
                artifacts = list(
                    session.exec(select(Artifact).order_by(Artifact.created_at.desc())),
                )

            for artifact in artifacts:
                with ui.card().classes("w-full"):
                    with ui.row().classes("items-center justify-between w-full"):
                        ui.label(artifact.title).classes("text-lg font-medium")
                        ui.badge(artifact.severity)
                    ui.label(artifact.artifact_type).classes("text-sm text-gray-500")
                    ui.label(artifact.summary)
                    if artifact.source_path:
                        ui.label(artifact.source_path).classes("text-sm")
                    with ui.expansion("Details", icon="article").classes("w-full"):
                        ui.json_editor({"content": {"json": artifact.data_json}})

            if not artifacts:
                ui.label("No artifacts yet.")
