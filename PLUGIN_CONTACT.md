# Plugin Contract

This document is the required reference for plugin authors.

## Hard Rules

- Do not write to the database directly.
- Do not import or call NiceGUI.
- Do not recursively scan the evidence root. Use the `EvidenceFile` records provided by the core scanner.
- Do not invent path formats. Use `relative_path`, `absolute_path`, and `virtual_path`.
- Return `ArtifactCreate` objects only.
- Let exceptions bubble up when a plugin cannot continue. The runner records plugin failure and continues with other plugins.
- Keep Windows compatibility. Avoid Linux-only dependencies and path assumptions.

## Plugin Kinds

### EvidencePlugin

Use this when the plugin needs to inspect the whole evidence item or a group of files.

Examples:

- `hash_manifest`
- `archive_index`
- `keyword_search`

### FilePlugin

Use this when the plugin operates on one file at a time.

Examples:

- `file_type`
- `metadata_extract`
- `browser_history`

## ArtifactCreate Fields

```text
artifact_type: str
title: str
summary: str
source_path: str | None
timestamp: datetime | None
severity: "info" | "low" | "medium" | "high"
is_key: bool
tags: list[str]
data: dict
```

Use common fields for display and search. Put plugin-specific details in `data`.

## Severity Guidance

- `info`: normal evidence facts such as manifest generation.
- `low`: notable but expected records.
- `medium`: suspicious findings, keyword hits, extension mismatch.
- `high`: strong key finding for the demonstration story.

## Required PR Contents

Every plugin PR must include:

- Plugin name and purpose.
- Supported inputs.
- Dependencies.
- Artifact types emitted.
- Minimal sample or sample description.
- Expected artifact examples.
- Windows test notes.

## Example Artifact

```python
ArtifactCreate(
    artifact_type="file.type_mismatch",
    title="Extension does not match detected type",
    summary="Downloads/photo.jpg appears to be a ZIP archive",
    source_path="Downloads/photo.jpg",
    timestamp=file.mtime,
    severity="medium",
    is_key=True,
    tags=["mismatch", "suspicious"],
    data={
        "extension": ".jpg",
        "detected_type": "application/zip",
    },
)
```
