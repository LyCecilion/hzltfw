from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from hzltfw.core.config import ExternalToolConfig


@dataclass(frozen=True)
class ToolHealth:
    name: str
    configured: bool
    available: bool
    message: str
    command: list[str]


@dataclass(frozen=True)
class ExternalRunResult:
    tool_name: str
    command: list[str]
    output_dir: Path
    return_code: int
    stdout: str
    stderr: str

    @property
    def success(self) -> bool:
        return self.return_code == 0


def check_tool_health(
    tool: ExternalToolConfig,
    *,
    timeout_seconds: int = 20,
) -> ToolHealth:
    if not tool.command:
        return ToolHealth(
            name=tool.name,
            configured=False,
            available=False,
            message="Command is not configured.",
            command=[],
        )
    executable = tool.command[0]
    if _resolve_executable(executable) is None:
        return ToolHealth(
            name=tool.name,
            configured=True,
            available=False,
            message=f"Executable not found: {executable}",
            command=tool.command,
        )

    try:
        completed = subprocess.run(
            [*tool.command, "--help"],
            cwd=_command_working_dir(tool.command),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return ToolHealth(
            name=tool.name,
            configured=True,
            available=False,
            message=str(exc),
            command=tool.command,
        )

    output = (completed.stdout or completed.stderr).strip()
    return ToolHealth(
        name=tool.name,
        configured=True,
        available=completed.returncode == 0,
        message=_first_line(output) or f"Exit code {completed.returncode}",
        command=tool.command,
    )


def run_external_tool(
    *,
    tool_name: str,
    command_prefix: list[str],
    arguments: list[str],
    output_dir: str | Path,
    timeout_seconds: int | None = None,
) -> ExternalRunResult:
    target_dir = Path(output_dir).expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)
    command = [*command_prefix, *arguments]
    completed = subprocess.run(
        command,
        cwd=_command_working_dir(command_prefix),
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        check=False,
    )
    return ExternalRunResult(
        tool_name=tool_name,
        command=command,
        output_dir=target_dir,
        return_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def _resolve_executable(executable: str) -> str | None:
    path = Path(executable)
    if path.is_absolute() or len(path.parts) > 1:
        return str(path) if path.exists() else None
    return shutil.which(executable)


def _command_working_dir(command_prefix: list[str]) -> Path | None:
    for value in reversed(command_prefix):
        path = Path(value)
        if path.exists() and path.is_file():
            return path.parent
    return None


def _first_line(value: str) -> str:
    return value.splitlines()[0] if value else ""
