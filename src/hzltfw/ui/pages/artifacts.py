from nicegui import ui
from sqlmodel import Session, select

from hzltfw.core.models import Artifact, PluginRun
from hzltfw.ui.artifact_views import render_artifact_view
from hzltfw.ui.pages.common import page_container, page_header, render_shell
from hzltfw.utils.i18n import t


def register_artifacts_page(engine) -> None:
    @ui.page("/artifacts")
    def artifacts_page() -> None:
        render_shell("artifacts")
        page_header(t("nav.discoveries"), step=4)

        with page_container():
            artifacts, plugin_names = _load_artifacts(engine)

            if not artifacts:
                with ui.element("div").classes("hz-empty-state mt-8"):
                    ui.label("🔍").classes("text-3xl mb-3")
                    ui.label(t("common.no_artifacts")).classes("text-sm")
                    ui.label("运行分析插件后，发现结果将在此处显示").classes(
                        "text-xs text-gray-400 mt-1"
                    )
                return

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
    key_count = sum(1 for a in artifacts if a.is_key)
    warning_count = sum(1 for a in artifacts if a.severity != "info")

    with ui.element("div").classes("hz-stat-row mb-6"):
        with ui.element("div").classes("hz-stat-card"):
            with ui.element("div").classes("hz-stat-icon hz-stat-icon--blue"):
                ui.label("📊").classes("text-lg")
            with ui.column().classes("gap-0"):
                ui.label(str(len(artifacts))).classes("hz-stat-value")
                ui.label("发现总数").classes("hz-stat-label")

        with ui.element("div").classes("hz-stat-card"):
            with ui.element("div").classes("hz-stat-icon hz-stat-icon--red"):
                ui.label("⚠️").classes("text-lg")
            with ui.column().classes("gap-0"):
                ui.label(str(key_count)).classes("hz-stat-value")
                ui.label("关键发现").classes("hz-stat-label")

        with ui.element("div").classes("hz-stat-card"):
            with ui.element("div").classes("hz-stat-icon hz-stat-icon--amber"):
                ui.label("🔔").classes("text-lg")
            with ui.column().classes("gap-0"):
                ui.label(str(warning_count)).classes("hz-stat-value")
                ui.label("需关注").classes("hz-stat-label")


def _render_filterable_artifacts(
    artifacts: list[Artifact],
    plugin_names: dict[int, str],
) -> None:
    artifact_types = sorted({a.artifact_type for a in artifacts})
    severities = sorted({a.severity for a in artifacts})
    plugins = sorted(set(plugin_names.values()))

    with ui.column().classes("w-full gap-3"):
        ui.label("筛选与审查").classes("hz-section-title")

        with ui.row().classes("w-full gap-3 flex-wrap items-end"):
            type_select = ui.select(
                options=["全部", *artifact_types],
                value="全部",
                label="类型",
            ).classes("min-w-40")
            severity_select = ui.select(
                options=["全部", *severities],
                value="全部",
                label="级别",
            ).classes("min-w-32")
            plugin_select = ui.select(
                options=["全部", *plugins],
                value="全部",
                label="插件",
            ).classes("min-w-40")
            key_only = ui.checkbox("仅关键发现", value=False)

        container = ui.column().classes("w-full gap-3")

        def refresh() -> None:
            container.clear()
            selected = [
                a
                for a in artifacts
                if _matches_filters(
                    artifact=a,
                    plugin_names=plugin_names,
                    artifact_type=type_select.value,
                    severity=severity_select.value,
                    plugin=plugin_select.value,
                    key_only=key_only.value,
                )
            ]
            with container:
                if not selected:
                    ui.label(t("common.no_artifacts")).classes("text-gray-400 text-sm")
                for artifact in selected:
                    _render_artifact_card(artifact, plugin_names)

        ui.button("应用过滤", on_click=refresh).props("color=primary")
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
        with ui.row().classes("items-start justify-between w-full"):
            with ui.column().classes("gap-1 flex-1"):
                ui.label(artifact.title).classes("text-base font-semibold")
                ui.label(artifact.summary).classes("text-sm text-gray-500")
            with ui.row().classes("gap-2 flex-shrink-0"):
                _severity_badge(artifact.severity)
                if artifact.is_key:
                    ui.badge("关键", color="red")

        with ui.row().classes("gap-3 text-xs text-gray-400 mt-3"):
            ui.label(artifact.artifact_type)
            ui.label(plugin_names.get(artifact.plugin_run_id, "unknown"))
            if artifact.source_path:
                ui.label(artifact.source_path)

        ui.separator().classes("my-3")
        render_artifact_view(artifact)


def _severity_badge(severity: str) -> None:
    color_map = {
        "info": "blue",
        "low": "green",
        "medium": "orange",
        "high": "red",
        "critical": "deep-purple",
    }
    ui.badge(severity, color=color_map.get(severity, "grey"))
