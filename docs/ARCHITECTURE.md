# Architecture

`hzltfw` uses a small core with normalized artifacts. Plugins perform analysis but do not own persistence or UI.

## Package Layout

```text
src/hzltfw/
  cli.py
  app.py
  core/
    database.py
    exceptions.py
    handoff.py
    models.py
    plugin.py
    report.py
    runner.py
    scanner.py
    workspace.py
  plugins/
    archive_index.py
    file_type.py
    hash_manifest.py
    keyword_search.py
    metadata_extract.py
  ui/
    pages/
      analysis.py
      artifacts.py
      cases.py
      evidence.py
      handoff.py
      reports.py
  utils/
    hashing.py
    timestamps.py
```

## Data Flow

1. User creates a case.
2. User adds evidence from a file or directory.
3. Core scanner indexes files into `evidence_files`.
4. Runner creates `plugin_runs`.
5. Plugins receive normalized evidence and file records.
6. Plugins return `ArtifactCreate` objects.
7. Runner persists artifacts and marks plugin status.
8. UI and reports read artifacts through common fields and `data_json`.

For Windows image or E01-based exercises, the handoff/intake helper inspects an
already exported directory and identifies recognizable Windows evidence sources.
It does not mount or parse disk images directly.

## Tables

```text
cases
- id
- case_no
- name
- investigator
- description
- created_at

evidence_items
- id
- case_id
- name
- source_path
- stored_path
- evidence_type
- size_bytes
- md5
- sha1
- sha256
- added_at
- operator
- metadata_json

evidence_files
- id
- evidence_id
- relative_path
- absolute_path
- virtual_path
- size_bytes
- mtime
- ctime
- sha256
- detected_type
- extension
- is_virtual
- parent_archive_path
- metadata_json

plugin_runs
- id
- case_id
- evidence_id
- plugin_name
- plugin_version
- status
- started_at
- finished_at
- error_message
- config_json

artifacts
- id
- case_id
- evidence_id
- plugin_run_id
- artifact_type
- title
- summary
- source_path
- timestamp
- severity
- is_key
- tags_json
- data_json
- created_at
```

## Artifact Design

Artifacts have stable common columns for search, report generation, and timeline generation. Plugin-specific data belongs in `data_json`.

Example:

```json
{
  "artifact_type": "hash.manifest",
  "title": "Evidence hash manifest",
  "summary": "Hashed 12 files",
  "source_path": null,
  "timestamp": null,
  "severity": "info",
  "data": {
    "file_count": 12,
    "total_size": 10240
  }
}
```

## Plugin Contracts

There are two plugin kinds:

- `EvidencePlugin`: analyzes an evidence item and the full indexed file list.
- `FilePlugin`: declares `supports(file)` and analyzes matching files.

Plugins must return `ArtifactCreate` values. They must not write to the database or call the GUI.

Built-in plugins currently cover file hashes, extension mismatch warnings,
regex-based keyword search, ZIP archive indexing, and image/PDF/DOCX metadata.

## Runner Behavior

- Each selected plugin gets a `plugin_runs` row.
- A plugin failure marks only that plugin run as failed.
- Other plugins continue.
- The runner is the only layer that persists artifacts.

## Report Structure

Markdown reports use this fixed structure:

1. Case information
2. Evidence information
3. Tool run records
4. Key findings
5. Timeline
6. Detailed results
7. Appendix

The full file manifest is optional because it can be large.
