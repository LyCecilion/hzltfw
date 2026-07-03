from __future__ import annotations

from pathlib import Path
from typing import Any

from nicegui import ui

from hzltfw.core.models import Artifact
from hzltfw.utils.i18n import t


def render_artifact_view(artifact: Artifact) -> None:
    if artifact.artifact_type == "keyword.regex_hit":
        _render_keyword_hit(artifact.data_json)
    elif artifact.artifact_type == "file.type_mismatch":
        _render_file_type_mismatch(artifact.data_json)
    elif artifact.artifact_type == "archive.index":
        _render_archive_index(artifact.data_json)
    elif artifact.artifact_type == "archive.entry":
        _render_archive_entry(artifact.data_json)
    elif artifact.artifact_type.startswith("metadata."):
        _render_metadata(artifact.data_json)
    elif artifact.artifact_type.startswith("external."):
        _render_external(artifact.data_json)
    elif artifact.artifact_type == "hash.manifest":
        _render_hash_manifest(artifact.data_json)
    else:
        ui.label(artifact.summary)

    with ui.expansion("高级 / 原始数据", icon="data_object").classes("w-full"):
        ui.json_editor({"content": {"json": artifact.data_json}})


def _render_keyword_hit(data: dict[str, Any]) -> None:
    _info_rows(
        [
            ("规则", data.get("rule")),
            ("行号", data.get("line_number")),
            ("命中文本", data.get("match")),
            ("上下文", data.get("snippet")),
        ],
    )


def _render_file_type_mismatch(data: dict[str, Any]) -> None:
    _info_rows(
        [
            ("原扩展名", data.get("extension")),
            ("检测扩展名", data.get("detected_extension")),
            ("MIME", data.get("detected_mime")),
            ("检测名称", data.get("detected_name")),
        ],
    )


def _render_archive_index(data: dict[str, Any]) -> None:
    _info_rows(
        [
            ("压缩包类型", data.get("archive_type")),
            ("条目数", data.get("entry_count")),
            ("文件数", data.get("file_count")),
            ("可疑条目数", data.get("suspicious_entry_count")),
        ],
    )
    entries = data.get("entries")
    if isinstance(entries, list) and entries:
        ui.table(
            columns=[
                {"name": "path", "label": "路径", "field": "path"},
                {"name": "size", "label": "大小", "field": "size"},
                {"name": "modified", "label": "修改时间", "field": "modified"},
            ],
            rows=[
                {
                    "path": entry.get("path"),
                    "size": entry.get("uncompressed_size"),
                    "modified": entry.get("modified_at"),
                }
                for entry in entries[:20]
                if isinstance(entry, dict)
            ],
        ).classes("w-full")


def _render_archive_entry(data: dict[str, Any]) -> None:
    entry = data.get("entry") if isinstance(data.get("entry"), dict) else {}
    _info_rows(
        [
            ("压缩包", data.get("archive_path")),
            ("内部路径", entry.get("path")),
            ("原因", ", ".join(data.get("reasons", []))),
            ("大小", entry.get("uncompressed_size")),
        ],
    )


def _render_metadata(data: dict[str, Any]) -> None:
    metadata = data.get("metadata") or data.get("exif") or data
    if isinstance(metadata, dict):
        _info_rows(list(metadata.items())[:20])
    else:
        ui.label(str(metadata))


def _render_external(data: dict[str, Any]) -> None:
    report_path = data.get("report_path")
    rows = [
        ("工具", data.get("tool_name")),
        ("输入类型", data.get("input_type")),
        ("输出目录", data.get("output_dir")),
        ("报告入口", report_path),
    ]
    _info_rows(rows)
    if isinstance(report_path, str) and Path(report_path).exists():
        ui.link("打开外部报告", Path(report_path).as_uri()).props("target=_blank")
    stdout = data.get("stdout")
    stderr = data.get("stderr")
    if stdout:
        with ui.expansion("stdout").classes("w-full"):
            ui.code(str(stdout)).classes("w-full")
    if stderr:
        with ui.expansion("stderr").classes("w-full"):
            ui.code(str(stderr)).classes("w-full")


def _render_hash_manifest(data: dict[str, Any]) -> None:
    _info_rows(
        [
            ("文件数", data.get("file_count")),
            ("总大小", data.get("total_size_bytes")),
            ("案件 ID", data.get("case_id")),
            ("证据 ID", data.get("evidence_id")),
        ],
    )


def _info_rows(rows: list[tuple[str, Any]]) -> None:
    clean_rows = [
        {"field": label, "value": _display_value(value)}
        for label, value in rows
        if value not in (None, "")
    ]
    if not clean_rows:
        ui.label(t("common.no_artifacts"))
        return
    ui.table(
        columns=[
            {"name": "field", "label": "字段", "field": "field"},
            {"name": "value", "label": "值", "field": "value"},
        ],
        rows=clean_rows,
    ).classes("w-full")


def _display_value(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    if isinstance(value, dict):
        return ", ".join(f"{key}: {item}" for key, item in value.items())
    return str(value)
