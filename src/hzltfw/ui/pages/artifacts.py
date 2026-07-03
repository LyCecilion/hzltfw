from nicegui import ui
from sqlmodel import Session, select

from hzltfw.core.models import Artifact, PluginRun
from hzltfw.ui.artifact_views import render_artifact_view
from hzltfw.ui.pages.common import page_container, render_nav
from hzltfw.utils.i18n import t


def register_artifacts_page(engine) -> None:
    @ui.page("/artifacts")
    def artifacts_page() -> None:
        render_nav()
        with page_container():
            ui.label(t("nav.discoveries")).classes("text-2xl font-semibold")
            artifacts, plugin_names = _load_artifacts(engine)
            _render_summary(artifacts)
            _render_filterable_artifacts(artifacts, plugin_names)


def _load_artifacts(engine) -> tuple[list[Artifact], dict[int, str]]:
    with Session(engine) as session:
        artifacts = list(
            session.exec(select(Artifact).order_by(Artifact.created_at.desc())),
        )
        runs = list(session.exec(select(PluginRun)))
    return artifacts, {run.id or 0: run.plugin_name for run in runs}


def _render_summary(artifacts: list[Artifact]) -> None:
    key_count = sum(1 for artifact in artifacts if artifact.is_key)
    warning_count = sum(1 for artifact in artifacts if artifact.severity != "info")
    with ui.row().classes("gap-3"):
        ui.badge(f"总数 {len(artifacts)}").props("outline")
        ui.badge(f"关键 {key_count}", color="red").props("outline")
        ui.badge(f"需关注 {warning_count}", color="orange").props("outline")


def _render_filterable_artifacts(
    artifacts: list[Artifact],
    plugin_names: dict[int, str],
) -> None:
    artifact_types = sorted({artifact.artifact_type for artifact in artifacts})
    severities = sorted({artifact.severity for artifact in artifacts})
    plugins = sorted(set(plugin_names.values()))
    with ui.column().classes("w-full gap-3"):
        with ui.row().classes("w-full gap-3"):
            type_select = ui.select(
                options=["全部", *artifact_types],
                value="全部",
                label="类型",
            ).classes("min-w-48")
            severity_select = ui.select(
                options=["全部", *severities],
                value="全部",
                label="级别",
            ).classes("min-w-40")
            plugin_select = ui.select(
                options=["全部", *plugins],
                value="全部",
                label="插件",
            ).classes("min-w-48")
            key_only = ui.checkbox("仅关键发现", value=False)
        container = ui.column().classes("w-full gap-3")

        def refresh() -> None:
            container.clear()
            selected = [
                artifact
                for artifact in artifacts
                if _matches_filters(
                    artifact=artifact,
                    plugin_names=plugin_names,
                    artifact_type=type_select.value,
                    severity=severity_select.value,
                    plugin=plugin_select.value,
                    key_only=key_only.value,
                )
            ]
            with container:
                if not selected:
                    ui.label(t("common.no_artifacts"))
                for artifact in selected:
                    _render_artifact_card(artifact, plugin_names)

        ui.button("应用过滤", on_click=refresh)
        refresh()


def _matches_filters(  # noqa: PLR0913
    *,
    artifact: Artifact,
    plugin_names: dict[int, str],
    artifact_type: str,
    severity: str,
    plugin: str,
    key_only: bool,
) -> bool:
    if artifact_type not in ("全部", artifact.artifact_type):
        return False
    if severity not in ("全部", artifact.severity):
        return False
    if plugin != "全部" and plugin_names.get(artifact.plugin_run_id) != plugin:
        return False
    return not key_only or artifact.is_key


def _render_artifact_card(
    artifact: Artifact,
    plugin_names: dict[int, str],
) -> None:
    with ui.card().classes("w-full"):
        with ui.row().classes("items-center justify-between w-full"):
            ui.label(artifact.title).classes("text-lg font-medium")
            with ui.row().classes("gap-2"):
                ui.badge(artifact.severity)
                if artifact.is_key:
                    ui.badge("关键", color="red")
        ui.label(artifact.summary)
        with ui.row().classes("gap-2 text-sm text-gray-500"):
            ui.label(artifact.artifact_type)
            ui.label(plugin_names.get(artifact.plugin_run_id, "unknown"))
            if artifact.source_path:
                ui.label(artifact.source_path)
        render_artifact_view(artifact)
