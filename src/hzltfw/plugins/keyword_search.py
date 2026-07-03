from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from hzltfw.core.models import EvidenceFile, EvidenceItem
from hzltfw.core.plugin import ArtifactCreate, PluginContext

DEFAULT_REGEXES = {
    "phone_cn": r"(?<!\d)1\d{10}(?!\d)",
    "email": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    "student_id": r"(?<!\d)252\d{8}(?!\d)",
}
DEFAULT_TEXT_EXTENSIONS = {
    ".csv",
    ".htm",
    ".html",
    ".json",
    ".log",
    ".md",
    ".rtf",
    ".text",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}
DEFAULT_MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024
DEFAULT_MAX_HITS_PER_FILE = 100
SNIPPET_RADIUS = 40


@dataclass(frozen=True)
class RegexRule:
    name: str
    pattern: re.Pattern[str]


class KeywordSearchPlugin:
    name = "keyword_search"
    version = "0.1.0"
    description = "Search text-like evidence files for demonstration regex hits."
    plugin_type = "evidence"
    artifact_types = ["keyword.regex_hit"]

    def analyze_evidence(
        self,
        context: PluginContext,
        evidence: EvidenceItem,
        files: list[EvidenceFile],
    ) -> list[ArtifactCreate]:
        del evidence

        rules = regex_rules(context.config)
        max_file_size = _int_config(
            context.config,
            "max_file_size_bytes",
            DEFAULT_MAX_FILE_SIZE_BYTES,
        )
        max_hits_per_file = _int_config(
            context.config,
            "max_hits_per_file",
            DEFAULT_MAX_HITS_PER_FILE,
        )

        artifacts: list[ArtifactCreate] = []
        for file in files:
            if not _supports_text_search(file, max_file_size):
                continue
            text = _read_text(Path(file.absolute_path or ""))
            if text is None:
                continue
            artifacts.extend(
                _search_file(
                    file=file,
                    text=text,
                    rules=rules,
                    max_hits=max_hits_per_file,
                ),
            )

        return artifacts


def regex_rules(config: dict[str, Any] | None = None) -> list[RegexRule]:
    config = config or {}
    configured = config.get("regexes") or DEFAULT_REGEXES
    if isinstance(configured, dict):
        items = configured.items()
    else:
        items = (
            (f"regex_{index + 1}", pattern)
            for index, pattern in enumerate(configured)
        )

    rules: list[RegexRule] = []
    for name, pattern in items:
        if not isinstance(name, str) or not isinstance(pattern, str):
            continue
        rules.append(RegexRule(name=name, pattern=re.compile(pattern)))
    return rules


def _int_config(config: dict[str, Any], key: str, default: int) -> int:
    value = config.get(key, default)
    return value if isinstance(value, int) and value > 0 else default


def _supports_text_search(file: EvidenceFile, max_file_size: int) -> bool:
    return (
        not file.is_virtual
        and file.absolute_path is not None
        and file.size_bytes <= max_file_size
        and file.extension.lower() in DEFAULT_TEXT_EXTENSIONS
    )


def _read_text(path: Path) -> str | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if b"\x00" in data[:4096]:
        return None
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return data.decode("utf-8", errors="replace")


def _search_file(
    file: EvidenceFile,
    text: str,
    rules: list[RegexRule],
    max_hits: int,
) -> list[ArtifactCreate]:
    artifacts: list[ArtifactCreate] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for rule in rules:
            for match in rule.pattern.finditer(line):
                artifacts.append(
                    _regex_hit_artifact(file, line_number, line, rule, match),
                )
                if len(artifacts) >= max_hits:
                    return artifacts
    return artifacts


def _regex_hit_artifact(
    file: EvidenceFile,
    line_number: int,
    line: str,
    rule: RegexRule,
    match: re.Match[str],
) -> ArtifactCreate:
    matched_text = match.group(0)
    snippet = _snippet(line, match.start(), match.end())
    return ArtifactCreate(
        artifact_type="keyword.regex_hit",
        title=f"Regex hit in {file.relative_path}",
        summary=(
            f"{rule.name} matched {matched_text} in {file.relative_path} "
            f"on line {line_number}."
        ),
        source_path=file.relative_path,
        timestamp=file.mtime,
        severity="medium",
        is_key=True,
        tags=["keyword", "regex", rule.name],
        data={
            "rule": rule.name,
            "pattern": rule.pattern.pattern,
            "line_number": line_number,
            "match": matched_text,
            "snippet": snippet,
        },
    )


def _snippet(line: str, start: int, end: int) -> str:
    left = max(start - SNIPPET_RADIUS, 0)
    right = min(end + SNIPPET_RADIUS, len(line))
    prefix = "..." if left > 0 else ""
    suffix = "..." if right < len(line) else ""
    return f"{prefix}{line[left:right].strip()}{suffix}"
