# Built-In Plugins

[中文](PLUGIN_TASKS.zh-CN.md)

This document records the final built-in plugin behavior for the coursework
release. It is no longer a pending task list.

## Common Rules

Every plugin follows the contract in `src/hzltfw/core/plugin.py`:

- Implement `EvidencePlugin` or `FilePlugin`.
- Return `ArtifactCreate` objects only.
- Do not write to the database directly.
- Do not import or call NiceGUI.
- Use the `EvidenceFile` records produced by the core scanner instead of
  recursively scanning evidence roots.
- Keep Windows-compatible path handling.

## Default Plugin Set

`src/hzltfw/core/runner.py` runs these plugins by default:

1. `hash_manifest`
2. `file_type`
3. `keyword_search`
4. `archive_index`
5. `metadata_extract`

The `external_forensics` adapter is not part of the default run. It is launched
manually from the Analysis page after the operator configures a tool command and
chooses a tool/input type.

## `hash_manifest`

Kind: `EvidencePlugin`

Purpose:

- Generate one manifest artifact for indexed physical files.
- Calculate MD5, SHA1, and SHA256.
- Include file size, relative path, virtual path, and timestamps.

Artifact types:

- `hash.manifest`

Expected artifact:

- Title: `Evidence hash manifest`
- Severity: `info`
- `data.files` contains one entry per hashed physical file.

## `file_type`

Kind: `FilePlugin`

Purpose:

- Detect file type from magic bytes with `puremagic`.
- Emit artifacts only when the extension and detected type disagree.
- Suppress normal matches to keep the discovery list useful.

Artifact types:

- `file.type_mismatch`

Expected artifact:

- Severity: `medium`
- `is_key`: `true`
- `data` records the original extension, detected extension, MIME type, detected
  name, and candidate extensions.

## `keyword_search`

Kind: `EvidencePlugin`

Purpose:

- Search text-like files with built-in demonstration regex rules.
- Default rules cover Chinese mobile numbers, email addresses, and demo student
  IDs.
- Skip virtual files, large files, and non-text extensions.
- Include the line number, matched text, and context snippet.

Artifact types:

- `keyword.regex_hit`

Expected artifact:

- Severity: `medium`
- `is_key`: `true`
- `source_path` points to the matched file.
- `data` includes `rule`, `pattern`, `line_number`, `match`, and `snippet`.

## `archive_index`

Kind: `EvidencePlugin`

Purpose:

- Index ZIP archive entries without extracting them.
- Produce one archive summary artifact per readable ZIP file.
- Emit key artifacts for suspicious entry names that match built-in keywords or
  the keyword-search regex rules.

Artifact types:

- `archive.index`
- `archive.entry`

Expected artifacts:

- `archive.index` records entry count, file count, directory count, suspicious
  entry count, and entry metadata.
- `archive.entry` uses severity `medium`, `is_key=true`, and records the
  archive path, entry data, and match reasons.

## `metadata_extract`

Kind: `FilePlugin`

Purpose:

- Extract image metadata with Pillow.
- Extract PDF document metadata and page count with `pypdf`.
- Extract DOCX core properties with `python-docx`.

Artifact types:

- `metadata.image`
- `metadata.pdf`
- `metadata.office`

Expected artifacts:

- Image artifacts include format, mode, dimensions, and EXIF data when present.
- PDF artifacts include metadata, page count, and parsed creation/modification
  timestamps when available.
- DOCX artifacts include core properties such as title, author, creation time,
  modification time, and comments when present.

## `external_forensics`

Kind: `EvidencePlugin`, launched manually

Purpose:

- Run locally configured ALEAPP, iLEAPP, or Hindsight commands.
- Keep external outputs in the case workspace.
- Emit report-link and highlight artifacts without importing full external
  result sets.

Artifact types:

- `external.report`
- `external.highlight`

Expected behavior:

- Missing commands are reported through health checks or failed plugin runs
  instead of breaking the default plugin flow.
- Commands are JSON string arrays and run with `shell=False`.
- Output is written under
  `.hzltfw/workspace/case-<case-id>/external_runs/<tool>/run-<plugin-run-id>/`.
- Report bundles copy external output folders and link them from `report.md`.
