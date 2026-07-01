from nicegui import ui
from sqlmodel import Session, select

from hzltfw.core.models import Case
from hzltfw.ui.pages.common import page_container, render_nav


def register_cases_page(engine) -> None:
    @ui.page("/")
    @ui.page("/cases")
    def cases_page() -> None:
        render_nav()
        with page_container():
            ui.label("Cases").classes("text-2xl font-semibold")

            with ui.card().classes("w-full"):
                ui.label("Create Case").classes("text-lg font-medium")
                case_no = ui.input("Case No").classes("w-full")
                name = ui.input("Name").classes("w-full")
                investigator = ui.input("Investigator").classes("w-full")
                description = ui.textarea("Description").classes("w-full")

                def create_case() -> None:
                    if not case_no.value or not name.value:
                        ui.notify("Case No and Name are required.", type="warning")
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
                    ui.notify("Case created.")
                    ui.navigate.reload()

                ui.button("Create", on_click=create_case)

            with Session(engine) as session:
                rows = list(session.exec(select(Case).order_by(Case.created_at.desc())))

            ui.table(
                columns=[
                    {"name": "case_no", "label": "Case No", "field": "case_no"},
                    {"name": "name", "label": "Name", "field": "name"},
                    {
                        "name": "investigator",
                        "label": "Investigator",
                        "field": "investigator",
                    },
                    {"name": "created_at", "label": "Created", "field": "created_at"},
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
