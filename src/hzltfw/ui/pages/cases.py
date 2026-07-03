from nicegui import ui
from sqlmodel import Session, select

from hzltfw.core.models import Case
from hzltfw.ui.pages.common import page_container, render_nav
from hzltfw.utils.i18n import t


def register_cases_page(engine) -> None:
    @ui.page("/")
    @ui.page("/cases")
    def cases_page() -> None:
        render_nav()
        with page_container():
            ui.label(t("cases.title")).classes("text-2xl font-semibold")

            with ui.card().classes("w-full"):
                ui.label(t("cases.create")).classes("text-lg font-medium")
                case_no = ui.input(t("cases.case_no")).classes("w-full")
                name = ui.input(t("cases.name")).classes("w-full")
                investigator = ui.input(t("cases.investigator")).classes("w-full")
                description = ui.textarea(t("cases.description")).classes("w-full")

                def create_case() -> None:
                    if not case_no.value or not name.value:
                        ui.notify(t("notify.case_required"), type="warning")
                        return
                    with Session(engine) as session:
                        session.add(
                            Case(
                                case_no=case_no.value,
                                name=name.value,
                                investigator=investigator.value or "",
                                description=description.value or "",
                            ),
                        )
                        session.commit()
                    ui.notify(t("notify.case_created"))
                    ui.navigate.reload()

                ui.button(t("common.create"), on_click=create_case)

            with Session(engine) as session:
                rows = list(session.exec(select(Case).order_by(Case.created_at.desc())))

            ui.table(
                columns=[
                    {
                        "name": "case_no",
                        "label": t("cases.case_no"),
                        "field": "case_no",
                    },
                    {"name": "name", "label": t("cases.name"), "field": "name"},
                    {
                        "name": "investigator",
                        "label": t("cases.investigator"),
                        "field": "investigator",
                    },
                    {
                        "name": "created_at",
                        "label": t("cases.created"),
                        "field": "created_at",
                    },
                ],
                rows=[
                    {
                        "case_no": row.case_no,
                        "name": row.name,
                        "investigator": row.investigator,
                        "created_at": row.created_at.isoformat(),
                    }
                    for row in rows
                ],
            ).classes("w-full")
