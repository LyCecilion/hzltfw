import json

from nicegui import ui
from sqlmodel import Session, select

from hzltfw.core.config import AppConfig, ExternalToolConfig, load_config, save_config
from hzltfw.core.external_probe import probe_external_input
from hzltfw.core.external_tools import check_tool_health
from hzltfw.core.models import EvidenceFile, EvidenceItem, PluginRun
from hzltfw.core.runner import run_plugins_for_evidence
from hzltfw.core.scanner import scan_evidence
from hzltfw.plugins.external_forensics import ExternalForensicsPlugin
from hzltfw.ui.pages.common import page_container, page_header, render_shell
from hzltfw.utils.i18n import t

EXTERNAL_TOOL_OPTIONS = {
    "aleapp": "ALEAPP - Android",
    "ileapp": "iLEAPP - iOS",
    "hindsight": "Hindsight - Browser",
}
INPUT_TYPE_OPTIONS = ["fs", "zip", "tar", "gz", "itunes", "file"]


class InvalidCommandJsonError(ValueError):
    def __str__(self) -> str:
        return "command must be a JSON string array"


def register_analysis_page(engine) -> None:
    @ui.page("/analysis")
    def analysis_page() -> None:
        render_shell("analysis")
        page_header(t("analysis.title"), step=3)

        with page_container():
            evidence_items, runs = _analysis_data(engine)
            evidence_options = _evidence_options(evidence_items)

            # ── Default Plugins Card ──
            with ui.card().classes("w-full"):
                ui.label(t("analysis.run_plugins")).classes(
                    "text-lg font-semibold mb-4"
                )
                evidence_select = ui.select(
                    options=evidence_options,
                    label=t("evidence.title"),
                    value=next(iter(evidence_options), None),
                ).classes("w-full max-w-sm")

                def run_analysis() -> None:
                    evidence_id = evidence_select.value
                    if not evidence_id:
                        ui.notify(t("notify.add_evidence_first"), type="warning")
                        return
                    with Session(engine) as session:
                        evidence = session.get(EvidenceItem, evidence_id)
                        if evidence is None:
                            ui.notify(t("notify.evidence_not_found"), type="negative")
                            return
                        if _first_indexed_file(session, evidence) is None:
                            scan_evidence(session, evidence)
                        run_plugins_for_evidence(session, evidence.id or 0)
                    ui.notify(t("notify.analysis_finished"))
                    ui.navigate.reload()

                ui.button(t("analysis.default_plugins"), on_click=run_analysis).props(
                    "color=primary mt-2"
                )

            # ── External Tools Card ──
            with ui.card().classes("w-full mt-4"):
                ui.label(t("analysis.external_tools")).classes(
                    "text-lg font-semibold mb-4"
                )

                with ui.row().classes("gap-4 w-full flex-wrap"):
                    evidence_select2 = ui.select(
                        options=evidence_options,
                        label=t("evidence.title"),
                        value=next(iter(evidence_options), None),
                    ).classes("min-w-40")
                    tool_select = ui.select(
                        options=EXTERNAL_TOOL_OPTIONS,
                        label=t("analysis.tool"),
                        value="aleapp",
                    ).classes("min-w-40")
                    input_type_select = ui.select(
                        options=INPUT_TYPE_OPTIONS,
                        label=t("analysis.input_type"),
                        value="fs",
                    ).classes("min-w-32")

                health_table = _external_health_table()
                suggestion_table = _external_suggestion_table()
                _render_command_config()
                _render_external_actions(
                    engine=engine,
                    evidence_select=evidence_select2,
                    tool_select=tool_select,
                    input_type_select=input_type_select,
                    health_table=health_table,
                    suggestion_table=suggestion_table,
                )
                _refresh_health_table(health_table)

            # ── Plugin Run History ──
            if runs:
                ui.label(f"{t('analysis.title')}  ·  运行记录").classes(
                    "hz-section-title mt-6"
                )
                _render_runs_table(runs)
            else:
                with ui.element("div").classes("hz-empty-state mt-8"):
                    ui.label("🔬").classes("text-3xl mb-3")
                    ui.label(t("common.no_artifacts")).classes("text-sm")


def _analysis_data(engine) -> tuple[list[EvidenceItem], list[PluginRun]]:
    with Session(engine) as session:
        evidence_items = list(session.exec(select(EvidenceItem)))
        runs = list(
            session.exec(select(PluginRun).order_by(PluginRun.started_at.desc())),
        )
    return evidence_items, runs


def _evidence_options(evidence_items: list[EvidenceItem]) -> dict[int | None, str]:
    return {
        evidence.id: f"#{evidence.id}  —  {evidence.name}"
        for evidence in evidence_items
    }


def _external_health_table():
    return ui.table(
        columns=[
            {"name": "tool", "label": "Tool", "field": "tool"},
            {"name": "available", "label": "Available", "field": "available"},
            {"name": "message", "label": "Message", "field": "message"},
        ],
        rows=[],
    ).classes("w-full")


def _external_suggestion_table():
    return ui.table(
        columns=[
            {"name": "tool", "label": "Suggested Tool", "field": "tool"},
            {"name": "confidence", "label": "Confidence", "field": "confidence"},
            {"name": "input_type", "label": "Input Type", "field": "input_type"},
            {"name": "reasons", "label": "Reasons", "field": "reasons"},
        ],
        rows=[],
    ).classes("w-full")


def _render_command_config() -> None:
    with ui.expansion(t("analysis.command_config")).classes("w-full"):
        config = load_config()
        command_inputs = {
            name: ui.input(
                label=f"{label} command JSON",
                value=json.dumps(
                    config.external_tools.get(
                        name,
                        ExternalToolConfig(name=name),
                    ).command,
                    ensure_ascii=False,
                ),
            ).classes("w-full")
            for name, label in EXTERNAL_TOOL_OPTIONS.items()
        }

        def save_tool_commands() -> None:
            try:
                tools = _updated_external_tools(command_inputs)
            except (json.JSONDecodeError, InvalidCommandJsonError) as exc:
                ui.notify(f"{t('notify.invalid_command')}: {exc}", type="negative")
                return
            current = load_config()
            save_config(AppConfig(language=current.language, external_tools=tools))
            ui.notify(t("notify.commands_saved"))
            ui.navigate.reload()

        ui.button(t("analysis.save_commands"), on_click=save_tool_commands)


def _render_external_actions(  # noqa: PLR0913
    *,
    engine,
    evidence_select,
    tool_select,
    input_type_select,
    health_table,
    suggestion_table,
) -> None:
    def probe_evidence() -> None:
        evidence = _selected_evidence(engine, evidence_select.value)
        if evidence is None:
            return
        result = probe_external_input(evidence.source_path)
        suggestion_table.rows = [
            {
                "tool": suggestion.tool_name,
                "confidence": f"{suggestion.confidence}%",
                "input_type": suggestion.input_type,
                "reasons": ", ".join(suggestion.reasons),
            }
            for suggestion in result.suggestions
        ]
        suggestion_table.update()
        if result.suggestions:
            best = result.suggestions[0]
            tool_select.value = best.tool_name
            input_type_select.value = best.input_type
            tool_select.update()
            input_type_select.update()
        ui.notify(f"Sampled {result.sampled_paths} paths.")

    def run_external() -> None:
        evidence = _selected_evidence(engine, evidence_select.value)
        if evidence is None:
            return
        with Session(engine) as session:
            plugin = ExternalForensicsPlugin(
                tool_select.value,
                input_type=input_type_select.value,
            )
            runs = run_plugins_for_evidence(
                session,
                evidence.id or 0,
                plugins=[plugin],
            )
        run = runs[0]
        if run.status == "failed":
            ui.notify(
                run.error_message or t("notify.external_failed"),
                type="negative",
            )
        else:
            ui.notify(t("notify.external_finished"))
        ui.navigate.reload()

    with ui.row().classes("gap-2 mt-4"):
        ui.button(
            t("analysis.check_tools"),
            on_click=lambda: _refresh_health_table(health_table),
        )
        ui.button(t("analysis.probe"), on_click=probe_evidence)
        ui.button(t("analysis.run_external"), on_click=run_external)


def _render_runs_table(runs: list[PluginRun]) -> None:
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
                "finished": run.finished_at.isoformat() if run.finished_at else "",
                "error": run.error_message or "",
            }
            for run in runs
        ],
    ).classes("w-full")


def _updated_external_tools(command_inputs) -> dict[str, ExternalToolConfig]:
    current = load_config()
    tools = dict(current.external_tools)
    for name, command_input in command_inputs.items():
        command = _parse_command_json(command_input.value or "[]")
        tools[name] = ExternalToolConfig(name=name, command=command)
    return tools


def _parse_command_json(value: str) -> list[str]:
    command = json.loads(value)
    if not isinstance(command, list) or not all(
        isinstance(item, str) and item for item in command
    ):
        raise InvalidCommandJsonError
    return command


def _refresh_health_table(health_table) -> None:
    current = load_config()
    health_table.rows = [
        {
            "tool": name,
            "available": "yes" if health.available else "no",
            "message": health.message,
        }
        for name in EXTERNAL_TOOL_OPTIONS
        for health in [
            check_tool_health(
                current.external_tools.get(name, ExternalToolConfig(name=name)),
            ),
        ]
    ]
    health_table.update()


def _selected_evidence(engine, evidence_id: int | None) -> EvidenceItem | None:
    if not evidence_id:
        ui.notify(t("notify.add_evidence_first"), type="warning")
        return None
    with Session(engine) as session:
        evidence = session.get(EvidenceItem, evidence_id)
    if evidence is None:
        ui.notify(t("notify.evidence_not_found"), type="negative")
    return evidence


def _first_indexed_file(
    session: Session,
    evidence: EvidenceItem,
) -> EvidenceFile | None:
    return session.exec(
        select(EvidenceFile).where(EvidenceFile.evidence_id == evidence.id),
    ).first()
