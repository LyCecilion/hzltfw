from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from hzltfw.core.config import ExternalToolConfig, load_config
from hzltfw.core.external_tools import run_external_tool
from hzltfw.core.models import EvidenceFile, EvidenceItem
from hzltfw.core.plugin import ArtifactCreate, PluginContext

SUPPORTED_TOOLS = ("aleapp", "ileapp", "hindsight")
LEAPP_INPUT_TYPES = {"fs", "zip", "tar", "gz"}
ILEAPP_EXTRA_INPUT_TYPES = {"itunes", "file"}
STDIO_LIMIT = 4000
MAX_HINDSIGHT_HIGHLIGHTS = 10


class UnsupportedExternalToolError(ValueError):
    def __str__(self) -> str:
        return "unsupported external tool"


class ExternalToolNotConfiguredError(RuntimeError):
    def __str__(self) -> str:
        return "external tool command is not configured"


class UnsupportedExternalInputTypeError(ValueError):
    def __str__(self) -> str:
        return "unsupported external tool input type"


class ExternalForensicsPlugin:
    version = "0.1.0"
    plugin_type = "evidence"
    artifact_types = ["external.report", "external.summary", "external.highlight"]

    def __init__(
        self,
        tool_name: str,
        *,
        input_type: str = "fs",
        tool_config: ExternalToolConfig | None = None,
    ) -> None:
        if tool_name not in SUPPORTED_TOOLS:
            raise UnsupportedExternalToolError
        self.tool_name = tool_name
        self.input_type = input_type
        self.name = f"external_{tool_name}"
        self.description = f"Run {tool_name} as an external forensic tool."
        self._tool_config = tool_config

    def analyze_evidence(
        self,
        context: PluginContext,
        evidence: EvidenceItem,
        files: list[EvidenceFile],
    ) -> list[ArtifactCreate]:
        del files

        tool_config = self._tool_config or load_config().external_tools.get(
            self.tool_name,
        )
        if tool_config is None or not tool_config.command:
            raise ExternalToolNotConfiguredError

        output_dir = _external_run_dir(context, self.tool_name)
        arguments = _tool_arguments(
            self.tool_name,
            input_path=Path(evidence.source_path),
            output_dir=output_dir,
            input_type=self.input_type,
        )
        result = run_external_tool(
            tool_name=self.tool_name,
            command_prefix=tool_config.command,
            arguments=arguments,
            output_dir=output_dir,
        )
        if not result.success:
            raise RuntimeError(_failure_message(result.stderr, result.stdout))

        report_path = _report_entry(self.tool_name, output_dir)
        artifacts = [
            _report_artifact(
                tool_name=self.tool_name,
                evidence=evidence,
                output_dir=output_dir,
                report_path=report_path,
                command=result.command,
                stdout=result.stdout,
                stderr=result.stderr,
                input_type=self.input_type,
            ),
        ]
        if self.tool_name == "hindsight":
            artifacts.extend(_hindsight_highlights(output_dir, evidence))
        return artifacts


def _tool_arguments(
    tool_name: str,
    *,
    input_path: Path,
    output_dir: Path,
    input_type: str,
) -> list[str]:
    if tool_name == "aleapp":
        _validate_input_type(tool_name, input_type, LEAPP_INPUT_TYPES)
        return ["-t", input_type, "-i", str(input_path), "-o", str(output_dir)]
    if tool_name == "ileapp":
        _validate_input_type(
            tool_name,
            input_type,
            LEAPP_INPUT_TYPES | ILEAPP_EXTRA_INPUT_TYPES,
        )
        return ["-t", input_type, "-i", str(input_path), "-o", str(output_dir)]
    output_prefix = output_dir / "hindsight"
    return [
        "-i",
        str(input_path),
        "-o",
        str(output_prefix),
        "-f",
        "jsonl",
        "-l",
        str(output_dir / "hindsight.log"),
    ]


def _validate_input_type(
    tool_name: str,
    input_type: str,
    supported: set[str],
) -> None:
    if input_type not in supported:
        raise UnsupportedExternalInputTypeError


def _external_run_dir(context: PluginContext, tool_name: str) -> Path:
    run_name = f"run-{context.plugin_run_id or context.evidence_id}"
    path = context.workspace_path / "external_runs" / tool_name / run_name
    path.mkdir(parents=True, exist_ok=True)
    return path


def _report_entry(tool_name: str, output_dir: Path) -> Path | None:
    if tool_name in {"aleapp", "ileapp"}:
        return next(output_dir.rglob("index.html"), None)
    for suffix in ("jsonl", "xlsx", "sqlite"):
        path = output_dir / f"hindsight.{suffix}"
        if path.exists():
            return path
    return None


def _report_artifact(  # noqa: PLR0913
    *,
    tool_name: str,
    evidence: EvidenceItem,
    output_dir: Path,
    report_path: Path | None,
    command: list[str],
    stdout: str,
    stderr: str,
    input_type: str,
) -> ArtifactCreate:
    report_value = str(report_path) if report_path else None
    return ArtifactCreate(
        artifact_type="external.report",
        title=f"{tool_name} external report",
        summary=f"{tool_name} completed for evidence '{evidence.name}'.",
        source_path=evidence.source_path,
        severity="info",
        tags=["external", tool_name, "report"],
        data={
            "tool_name": tool_name,
            "input_type": input_type,
            "output_dir": str(output_dir),
            "report_path": report_value,
            "command": command,
            "stdout": _trim_stdio(stdout),
            "stderr": _trim_stdio(stderr),
        },
    )


def _hindsight_highlights(
    output_dir: Path,
    evidence: EvidenceItem,
) -> list[ArtifactCreate]:
    jsonl_path = output_dir / "hindsight.jsonl"
    if not jsonl_path.exists():
        return []

    highlights: list[ArtifactCreate] = []
    for index, record in enumerate(_read_jsonl(jsonl_path), start=1):
        if index > MAX_HINDSIGHT_HIGHLIGHTS:
            break
        title = str(record.get("url") or record.get("name") or "Hindsight item")
        highlights.append(
            ArtifactCreate(
                artifact_type="external.highlight",
                title=f"Hindsight highlight: {title}",
                summary=str(record.get("interpretation") or record.get("type") or ""),
                source_path=evidence.source_path,
                severity="low",
                tags=["external", "hindsight", "highlight"],
                data={"tool_name": "hindsight", "record": record},
            ),
        )
    return highlights


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            records.append(value)
    return records


def _failure_message(stderr: str, stdout: str) -> str:
    detail = _trim_stdio(stderr or stdout)
    return detail or "External tool failed."


def _trim_stdio(value: str) -> str:
    if len(value) <= STDIO_LIMIT:
        return value
    return value[:STDIO_LIMIT] + "\n...[truncated]"
