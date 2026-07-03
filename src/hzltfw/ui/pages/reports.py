from pathlib import Path

from nicegui import ui
from sqlmodel import Session, select

from hzltfw.core.models import Case
from hzltfw.core.report import export_case_markdown, export_case_report_bundle
from hzltfw.ui.pages.common import page_container, render_nav
from hzltfw.utils.i18n import t


def register_reports_page(engine) -> None:
    @ui.page("/reports")
    def reports_page() -> None:
        render_nav()
        with page_container():
            ui.label(t("reports.title")).classes("text-2xl font-semibold")

            with Session(engine) as session:
                cases = list(
                    session.exec(select(Case).order_by(Case.created_at.desc())),
                )

            case_options = {case.id: f"{case.case_no} - {case.name}" for case in cases}
            with ui.card().classes("w-full"):
                case_select = ui.select(
                    options=case_options,
                    label=t("evidence.case"),
                    value=next(iter(case_options), None),
                ).classes("w-full")
                include_manifest = ui.checkbox(
                    t("reports.include_manifest"),
                    value=False,
                )
                output_path = ui.input(
                    t("reports.output_path"),
                    value=str(Path("reports") / "case-report.md"),
                ).classes("w-full")
                bundle_path = ui.input(
                    t("reports.bundle_dir"),
                    value=str(Path("reports") / "case-report-bundle"),
                ).classes("w-full")

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

                ui.button(t("reports.export_markdown"), on_click=export_report)

                def export_bundle() -> None:
                    if not case_select.value:
                        ui.notify(t("notify.create_case_first"), type="warning")
                        return
                    with Session(engine) as session:
                        path = export_case_report_bundle(
                            session,
                            case_select.value,
                            bundle_path.value,
                            include_manifest=include_manifest.value,
                        )
                    ui.notify(f"{t('notify.bundle_exported')}: {path}")

                ui.button(t("reports.export_bundle"), on_click=export_bundle)
