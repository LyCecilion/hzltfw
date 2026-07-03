# Plugin Tasks

[中文](PLUGIN_TASKS.zh-CN.md)

This file defines the expected plugin work for the MVP. Use it to create GitHub issues and PR checklists.

## Common Completion Rules

Every plugin must:

- Implement `EvidencePlugin` or `FilePlugin` from `src/hzltfw/core/plugin.py`.
- Return `ArtifactCreate` objects only.
- Avoid direct database writes.
- Avoid GUI imports.
- Use `EvidenceFile.relative_path`, `absolute_path`, and `virtual_path` instead of rescanning evidence roots.
- Add at least one test or update `tests/test_smoke.py` with a minimal sample.
- Document emitted artifact types in the PR.
- Run on Windows.

## `hash_manifest`

Status: implemented as the first `EvidencePlugin` example.

Purpose:

- Generate a manifest for all indexed physical files.
- Calculate MD5, SHA1, and SHA256.
- Include file size and timestamps.

Artifact types:

- `hash.manifest`

MVP done when:

- A directory evidence item produces one manifest artifact.
- The report can include full manifest details when `include_manifest` is enabled.

## `file_type`

Status: implemented as the first `FilePlugin` example.

Purpose:

- Detect file type from magic bytes.
- Flag extension mismatch as a key warning artifact.
- Suppress normal extension matches to avoid noisy artifact lists.

Artifact types:

- `file.type_mismatch`

MVP done when:

- Normal files do not produce artifacts when their extension matches detected type.
- A fake file such as `fake.jpg` with PDF or ZIP bytes produces `file.type_mismatch`.
- Mismatch artifacts use `severity="medium"` and `is_key=True`.

## `keyword_search`

Status: implemented as an `EvidencePlugin` with built-in demo regex rules.

Plugin kind: `EvidencePlugin`.

Purpose:

- Search text-like files for configured keywords.
- Support simple regex patterns.
- Include a short context snippet around each hit.
- Skip large binary files by default.

Suggested config:

```json
{
  "keywords": ["泄露", "密码", "课程资料"],
  "regexes": ["[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}"]
}
```

Artifact types:

- `keyword.hit`
- `keyword.regex_hit`

MVP done when:

- A `.txt` sample with a keyword produces a hit artifact.
- A sample email address produces a regex hit artifact.
- Artifacts include `source_path`, `line_number`, `match`, and `snippet` in `data`.

## `archive_index`

Status: implemented for ZIP indexing without extraction.

Plugin kind: `EvidencePlugin`.

Purpose:

- Index ZIP files first.
- Add TAR support if time allows.
- Add 7z support through `py7zr` only after ZIP/TAR are stable.
- Do not auto-extract archive contents in MVP.

Artifact types:

- `archive.index`
- `archive.entry`

MVP done when:

- A ZIP sample produces an archive summary artifact.
- Archive entries include path, uncompressed size, compressed size if available, and modified time if available.
- Suspicious entry names can be marked with tags such as `keyword` or `suspicious_name`.

## `metadata_extract`

Status: implemented for image, PDF, and DOCX metadata.

Plugin kind: `FilePlugin`.

Purpose:

- Extract image metadata through Pillow.
- Extract PDF document metadata through `pypdf`.
- Extract basic Office metadata if time allows.

Artifact types:

- `metadata.image`
- `metadata.pdf`
- `metadata.office`

MVP done when:

- A JPEG with EXIF produces camera/time metadata.
- A PDF sample produces title, author, creator, producer, and page count if available.
- Metadata artifacts use timestamp fields when reliable metadata time exists.

## `browser_history`

Bonus task. Do not let it block the main flow.

Plugin kind: `FilePlugin`.

Purpose:

- Detect Chromium `History` SQLite databases.
- Parse URL visits.
- Optionally parse downloads if time allows.
- Normalize Chromium timestamps.

Artifact types:

- `browser.history`
- `browser.download`

MVP done when:

- A prepared Chromium `History` sample produces visit artifacts.
- Each visit artifact includes URL, title, visit time, visit count if available, and source database path.
- Artifacts can appear in the report timeline.

Cut rule:

- If not stable by Day 5, keep the plugin planned or experimental and remove it from the live demo path.
