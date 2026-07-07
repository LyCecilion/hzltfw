from pathlib import Path

from nicegui import ui
from sqlmodel import Session, select

from hzltfw.core.models import Case
from hzltfw.core.report import export_case_markdown, export_case_report_bundle
from hzltfw.ui.pages.common import page_container, page_header, render_shell
from hzltfw.utils.i18n import t


def register_reports_page(engine) -> None:
    @ui.page("/reports")
    def reports_page() -> None:
        render_shell("reports")
        page_header(t("reports.title"), step=5)

        with page_container():
            with Session(engine) as session:
                cases = list(
                    session.exec(select(Case).order_by(Case.created_at.desc())),
                )

            case_options = {
                case.id: f"{case.case_no}  —  {case.name}" for case in cases
            }

            if not cases:
                with ui.element("div").classes("hz-empty-state mt-8"):
                    ui.label("📝").classes("text-3xl mb-3")
                    ui.label("请先创建案件并完成分析").classes("text-sm")
                return

            # ── Export Markdown Card ──
            with ui.card().classes("w-full"):
                ui.label(t("reports.export_markdown")).classes(
                    "text-lg font-semibold mb-4"
                )
                with ui.row().classes("gap-4 w-full flex-wrap"):
                    case_select = ui.select(
                        options=case_options,
                        label=t("evidence.case"),
                        value=next(iter(case_options), None),
                    ).classes("min-w-64")
                    output_path = ui.input(
                        t("reports.output_path"),
                        value=str(Path("reports") / "case-report.md"),
                    ).classes("min-w-72 flex-1")

                include_manifest = ui.checkbox(
                    t("reports.include_manifest"), value=False
                ).classes("mt-2")

                def export_report() -> None:
                    if not case_select.value:
                        ui.notify(t("notify.create_case_first"), type="warning")
                        return
                    with Session(engine) as session:
                        path = export_case_markdown(
                            session,
                            case_select.value,
                            output_path.value,
                            include_manifest=include_manifest.value,
                        )
                    ui.notify(f"{t('notify.report_exported')}: {path}")

                ui.button(t("reports.export_markdown"), on_click=export_report).props(
                    "color=primary mt-3"
                )

            # ── Export Bundle Card ──
            with ui.card().classes("w-full mt-4"):
                ui.label(t("reports.export_bundle")).classes(
                    "text-lg font-semibold mb-4"
                )
                with ui.row().classes("gap-4 w-full flex-wrap"):
                    case_select2 = ui.select(
                        options=case_options,
                        label=t("evidence.case"),
                        value=next(iter(case_options), None),
                    ).classes("min-w-64")
                    bundle_path = ui.input(
                        t("reports.bundle_dir"),
                        value=str(Path("reports") / "case-report-bundle"),
                    ).classes("min-w-72 flex-1")

                include_manifest2 = ui.checkbox(
                    t("reports.include_manifest"), value=False
                ).classes("mt-2")

                def export_bundle() -> None:
                    if not case_select2.value:
                        ui.notify(t("notify.create_case_first"), type="warning")
                        return
                    with Session(engine) as session:
                        path = export_case_report_bundle(
                            session,
                            case_select2.value,
                            bundle_path.value,
                            include_manifest=include_manifest2.value,
                        )
                    ui.notify(f"{t('notify.bundle_exported')}: {path}")

                ui.button(t("reports.export_bundle"), on_click=export_bundle).props(
                    "color=primary mt-3"
                )
