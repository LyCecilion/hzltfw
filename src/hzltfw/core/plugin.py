from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Literal, Protocol

from hzltfw.core.models import EvidenceFile, EvidenceItem, Severity

PluginKind = Literal["evidence", "file"]


@dataclass(frozen=True)
class ArtifactCreate:
    artifact_type: str
    title: str
    summary: str = ""
    source_path: str | None = None
    timestamp: datetime | None = None
    severity: Severity = "info"
    is_key: bool = False
    tags: list[str] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PluginContext:
    case_id: int
    evidence_id: int
    workspace_path: Path
    config: dict[str, Any] = field(default_factory=dict)


class BasePlugin(Protocol):
    name: str
    version: str
    description: str
    plugin_type: PluginKind
    artifact_types: list[str]


class EvidencePlugin(BasePlugin, Protocol):
    plugin_type: Literal["evidence"]

    def analyze_evidence(
        self,
        context: PluginContext,
        evidence: EvidenceItem,
        files: list[EvidenceFile],
    ) -> list[ArtifactCreate]:
        """Analyze an evidence item and its indexed files."""


class FilePlugin(BasePlugin, Protocol):
    plugin_type: Literal["file"]

    def supports(self, file: EvidenceFile) -> bool:
        """Return whether this plugin can analyze the given file."""

    def analyze_file(
        self,
        context: PluginContext,
        evidence: EvidenceItem,
        file: EvidenceFile,
    ) -> list[ArtifactCreate]:
        """Analyze one indexed file."""
