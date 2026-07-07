from nicegui import ui
from sqlmodel import Session, select

from hzltfw.core.models import Case
from hzltfw.core.records import delete_case_record
from hzltfw.ui.pages.common import (
    confirm_action,
    page_container,
    page_header,
    render_shell,
)
from hzltfw.utils.i18n import t


def register_cases_page(engine) -> None:
    @ui.page("/")
    @ui.page("/cases")
    def cases_page() -> None:
        render_shell("cases")
        page_header(t("cases.title"), step=1)

        with page_container():
            # ── Create Case Card ──
            with ui.card().classes("w-full"):
                ui.label(t("cases.create")).classes("text-lg font-semibold mb-4")
                with ui.row().classes("gap-4 w-full flex-wrap"):
                    case_no = ui.input(t("cases.case_no")).classes("min-w-48")
                    name = ui.input(t("cases.name")).classes("min-w-48 flex-1")
                with ui.row().classes("gap-4 w-full flex-wrap mt-2"):
                    investigator = ui.input(t("cases.investigator")).classes("min-w-48")
                description = ui.textarea(t("cases.description")).classes("w-full mt-2")

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

                ui.button(t("common.create"), on_click=create_case).props(
                    "color=primary"
                )

            # ── Case List ──
            with Session(engine) as session:
                rows = list(session.exec(select(Case).order_by(Case.created_at.desc())))

            if rows:
                ui.label(f"{t('cases.title')}  ·  {len(rows)} 个案件").classes(
                    "hz-section-title mt-6"
                )
                rows_by_id = {row.id or 0: row for row in rows}

                def request_delete(event) -> None:
                    case_id = int(event.args)
                    case = rows_by_id.get(case_id)
                    if case is None:
                        return

                    def delete_case() -> None:
                        with Session(engine) as session:
                            deleted = delete_case_record(session, case_id)
                        if deleted:
                            ui.notify(t("notify.case_deleted"))
                            ui.navigate.reload()

                    confirm_action(
                        title=t("cases.delete"),
                        message=t("cases.delete_confirm").format(
                            case=f"{case.case_no}  —  {case.name}"
                        ),
                        confirm_label=t("common.delete"),
                        on_confirm=delete_case,
                    )

                table = ui.table(
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
                        {
                            "name": "actions",
                            "label": t("common.actions"),
                            "field": "actions",
                        },
                    ],
                    rows=[
                        {
                            "id": row.id,
                            "case_no": row.case_no,
                            "name": row.name,
                            "investigator": row.investigator,
                            "created_at": row.created_at.isoformat(),
                            "actions": "",
                        }
                        for row in rows
                    ],
                ).classes("w-full")
                table.add_slot(
                    "body-cell-actions",
                    """
                    <q-td :props="props">
                      <q-btn dense flat round color="negative" icon="delete"
                        @click.stop="$parent.$emit('delete-row', props.row.id)" />
                    </q-td>
                    """,
                )
                table.on("delete-row", request_delete)
            else:
                with ui.element("div").classes("hz-empty-state mt-8"):
                    ui.label("📋").classes("text-3xl mb-3")
                    ui.label(t("common.no_artifacts")).classes("text-sm")
