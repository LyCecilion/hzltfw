from __future__ import annotations

import tarfile
from dataclasses import dataclass
from pathlib import Path
from zipfile import BadZipFile, ZipFile, is_zipfile

MAX_PROBE_PATHS = 5000

ANDROID_HINTS = (
    "data/data/",
    "data/user/0/",
    "sdcard/",
    "system/",
    "packages.xml",
    "com.android.",
)
IOS_HINTS = (
    "manifest.db",
    "info.plist",
    "homedomain/",
    "mediadomain/",
    "appdomain-",
    "private/var/mobile/",
)
CHROMIUM_HINTS = (
    "/history",
    "default/history",
    "profile 1/history",
    "cookies",
    "login data",
    "web data",
)


@dataclass(frozen=True)
class ProbeResult:
    input_path: Path
    input_type: str
    suggestions: list[ToolSuggestion]
    sampled_paths: int


@dataclass(frozen=True)
class ToolSuggestion:
    tool_name: str
    confidence: int
    input_type: str
    reasons: list[str]
    warning: str = ""


def probe_external_input(path: str | Path) -> ProbeResult:
    input_path = Path(path).expanduser().resolve()
    input_type, members = _sample_paths(input_path)
    suggestions = sorted(
        (
            suggestion
            for suggestion in (
                _suggest("aleapp", input_type, members, ANDROID_HINTS),
                _suggest("ileapp", input_type, members, IOS_HINTS),
                _suggest("hindsight", input_type, members, CHROMIUM_HINTS),
            )
            if suggestion.confidence > 0
        ),
        key=lambda item: item.confidence,
        reverse=True,
    )
    return ProbeResult(
        input_path=input_path,
        input_type=input_type,
        suggestions=suggestions,
        sampled_paths=len(members),
    )


def _sample_paths(path: Path) -> tuple[str, list[str]]:
    if path.is_dir():
        return "fs", _sample_directory(path)
    if is_zipfile(path):
        return "zip", _sample_zip(path)
    if tarfile.is_tarfile(path):
        return "tar", _sample_tar(path)
    if path.suffix.lower() == ".gz":
        return "gz", [path.name.lower()]
    if path.is_file():
        return "file", [path.name.lower()]
    return "unknown", []


def _sample_directory(path: Path) -> list[str]:
    paths: list[str] = []
    for child in sorted(path.rglob("*")):
        paths.append(child.relative_to(path).as_posix().lower())
        if len(paths) >= MAX_PROBE_PATHS:
            break
    return paths


def _sample_zip(path: Path) -> list[str]:
    try:
        with ZipFile(path) as archive:
            return [
                name.lower()
                for name in archive.namelist()[:MAX_PROBE_PATHS]
                if name and not name.endswith("/")
            ]
    except (BadZipFile, OSError):
        return []


def _sample_tar(path: Path) -> list[str]:
    try:
        with tarfile.open(path) as archive:
            names = archive.getnames()
    except (tarfile.TarError, OSError):
        return []
    return [name.lower() for name in names[:MAX_PROBE_PATHS] if name]


def _suggest(
    tool_name: str,
    input_type: str,
    members: list[str],
    hints: tuple[str, ...],
) -> ToolSuggestion:
    reasons = _matching_hints(members, hints)
    if not reasons:
        return ToolSuggestion(
            tool_name=tool_name,
            confidence=0,
            input_type=input_type,
            reasons=[],
        )
    confidence = min(95, 35 + len(reasons) * 15)
    warning = ""
    if tool_name == "hindsight" and input_type == "file":
        warning = "Hindsight works best with a browser profile directory."
    return ToolSuggestion(
        tool_name=tool_name,
        confidence=confidence,
        input_type=input_type,
        reasons=reasons,
        warning=warning,
    )


def _matching_hints(members: list[str], hints: tuple[str, ...]) -> list[str]:
    matches: list[str] = []
    for hint in hints:
        if any(hint in member for member in members):
            matches.append(hint)
    return matches
