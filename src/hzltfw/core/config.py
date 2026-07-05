from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

DEFAULT_LANGUAGE = "zh-CN"
DEFAULT_CONFIG_PATH = Path(".hzltfw") / "config.json"
PORTABLE_APPS_ROOT = Path("/home/lycecilion/Workspace/PortableApps")


@dataclass(frozen=True)
class ExternalToolConfig:
    name: str
    command: list[str] = field(default_factory=list)
    enabled: bool = True


@dataclass(frozen=True)
class AppConfig:
    language: str = DEFAULT_LANGUAGE
    external_tools: dict[str, ExternalToolConfig] = field(default_factory=dict)


def load_config(path: str | Path = DEFAULT_CONFIG_PATH) -> AppConfig:
    config_path = Path(path)
    if not config_path.exists():
        return default_config()

    data = json.loads(config_path.read_text(encoding="utf-8"))
    return _config_from_data(data)


def save_config(
    config: AppConfig,
    path: str | Path = DEFAULT_CONFIG_PATH,
) -> Path:
    config_path = Path(path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        json.dumps(_config_to_data(config), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return config_path


def default_config() -> AppConfig:
    return AppConfig(external_tools=default_external_tools())


def default_external_tools() -> dict[str, ExternalToolConfig]:
    candidates = {
        "aleapp": PORTABLE_APPS_ROOT / "ALEAPP",
        "ileapp": PORTABLE_APPS_ROOT / "ILEAPP",
        "hindsight": PORTABLE_APPS_ROOT / "hindsight",
    }
    tools: dict[str, ExternalToolConfig] = {}
    for name, tool_dir in candidates.items():
        script = tool_dir / f"{name}.py"
        command = _python_script_command(tool_dir, script) if script.exists() else []
        tools[name] = ExternalToolConfig(name=name, command=command)
    return tools


def _python_script_command(tool_dir: Path, script: Path) -> list[str]:
    venv_python = _venv_python(tool_dir)
    if venv_python is not None:
        return [str(venv_python), str(script)]
    return ["python", str(script)]


def _venv_python(tool_dir: Path) -> Path | None:
    candidates = (
        tool_dir / ".venv" / "bin" / "python",
        tool_dir / "venv" / "bin" / "python",
        tool_dir / ".venv" / "Scripts" / "python.exe",
        tool_dir / "venv" / "Scripts" / "python.exe",
    )
    return next((path for path in candidates if path.exists()), None)


def _config_from_data(data: dict[str, Any]) -> AppConfig:
    configured_tools = data.get("external_tools", {})
    default_tools = default_external_tools()
    external_tools = {
        name: _tool_from_data(name, configured_tools.get(name), default_tool)
        for name, default_tool in default_tools.items()
    }
    for name, value in configured_tools.items():
        if name not in external_tools:
            external_tools[name] = _tool_from_data(name, value, None)

    language = data.get("language", DEFAULT_LANGUAGE)
    return AppConfig(
        language=language if isinstance(language, str) else DEFAULT_LANGUAGE,
        external_tools=external_tools,
    )


def _tool_from_data(
    name: str,
    data: Any,
    default_tool: ExternalToolConfig | None,
) -> ExternalToolConfig:
    if not isinstance(data, dict):
        return default_tool or ExternalToolConfig(name=name)
    command = data.get("command")
    enabled = data.get("enabled", True)
    return ExternalToolConfig(
        name=name,
        command=command
        if _is_command(command)
        else default_tool.command
        if default_tool
        else [],
        enabled=enabled if isinstance(enabled, bool) else True,
    )


def _is_command(value: Any) -> bool:
    return isinstance(value, list) and all(
        isinstance(item, str) and item for item in value
    )


def _config_to_data(config: AppConfig) -> dict[str, Any]:
    return {
        "language": config.language,
        "external_tools": {
            name: asdict(tool) for name, tool in config.external_tools.items()
        },
    }
