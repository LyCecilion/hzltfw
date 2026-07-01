from datetime import datetime
from typing import Any, Literal

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

from hzltfw.utils.timestamps import utc_now

Severity = Literal["info", "low", "medium", "high"]
PluginStatus = Literal["running", "success", "failed"]
EvidenceType = Literal["file", "directory"]


class Case(SQLModel, table=True):
    __tablename__ = "cases"

    id: int | None = Field(default=None, primary_key=True)
    case_no: str = Field(index=True, unique=True)
    name: str
    investigator: str = ""
    description: str = ""
    created_at: datetime = Field(default_factory=utc_now, index=True)


class EvidenceItem(SQLModel, table=True):
    __tablename__ = "evidence_items"

    id: int | None = Field(default=None, primary_key=True)
    case_id: int = Field(foreign_key="cases.id", index=True)
    name: str
    source_path: str
    stored_path: str | None = None
    evidence_type: str
    size_bytes: int = 0
    md5: str | None = None
    sha1: str | None = None
    sha256: str | None = None
    added_at: datetime = Field(default_factory=utc_now, index=True)
    operator: str = ""
    metadata_json: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
    )


class EvidenceFile(SQLModel, table=True):
    __tablename__ = "evidence_files"

    id: int | None = Field(default=None, primary_key=True)
    evidence_id: int = Field(foreign_key="evidence_items.id", index=True)
    relative_path: str
    absolute_path: str | None = None
    virtual_path: str
    size_bytes: int = 0
    mtime: datetime | None = Field(default=None, index=True)
    ctime: datetime | None = Field(default=None, index=True)
    sha256: str | None = Field(default=None, index=True)
    detected_type: str | None = None
    extension: str = ""
    is_virtual: bool = False
    parent_archive_path: str | None = None
    metadata_json: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
    )


class PluginRun(SQLModel, table=True):
    __tablename__ = "plugin_runs"

    id: int | None = Field(default=None, primary_key=True)
    case_id: int = Field(foreign_key="cases.id", index=True)
    evidence_id: int | None = Field(default=None, foreign_key="evidence_items.id")
    plugin_name: str = Field(index=True)
    plugin_version: str
    status: str = Field(default="running", index=True)
    started_at: datetime = Field(default_factory=utc_now, index=True)
    finished_at: datetime | None = None
    error_message: str | None = None
    config_json: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
    )


class Artifact(SQLModel, table=True):
    __tablename__ = "artifacts"

    id: int | None = Field(default=None, primary_key=True)
    case_id: int = Field(foreign_key="cases.id", index=True)
    evidence_id: int | None = Field(default=None, foreign_key="evidence_items.id")
    plugin_run_id: int = Field(foreign_key="plugin_runs.id", index=True)
    artifact_type: str = Field(index=True)
    title: str
    summary: str = ""
    source_path: str | None = Field(default=None, index=True)
    timestamp: datetime | None = Field(default=None, index=True)
    severity: str = Field(default="info", index=True)
    is_key: bool = Field(default=False, index=True)
    tags_json: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    data_json: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
    )
    created_at: datetime = Field(default_factory=utc_now, index=True)
