# Hazelita Forensics Workbench

[中文](README.zh-CN.md)

`hzltfw` is a local digital forensics workbench for electronic data forensics course practice. The first deliverable focuses on a stable live-demonstration flow: create a case, add a prepared Windows-style evidence sample, run analysis plugins, inspect artifacts in a GUI, and export a Markdown report.

## MVP Flow

1. Create a case.
2. Add file or directory evidence.
3. Scan evidence into `evidence_files`.
4. Run selected analysis plugins.
5. Store normalized artifacts.
6. Review artifacts and timeline-capable results in the GUI.
7. Export a Markdown forensics report.

## Technology

- Python 3.12+
- uv
- NiceGUI
- SQLite
- SQLModel
- ruff
- pytest
- Optional Nix development shell through `flake.nix`

## Development

```bash
uv sync --dev
uv run hzltfw
```

Run checks:

```bash
uv run ruff check .
uv run pytest
```

## Collaboration

All feature work goes through pull requests. Do not push directly to `main`.
See [CONTRIBUTING.md](CONTRIBUTING.md) for the lightweight Git workflow,
branch naming rules, PR checklist, and AI coding rules.

Plugin work should follow [PLUGIN_CONTACT.md](PLUGIN_CONTACT.md) and
[PLUGIN_TASKS.md](PLUGIN_TASKS.md).
For Windows image or E01-based coursework, export selected files first and use
[EVIDENCE_HANDOFF.md](EVIDENCE_HANDOFF.md) to inspect the exported directory.

With Determinate Nix or another flakes-enabled Nix:

```bash
nix develop
uv sync --dev
```

## Planned Tool Capabilities

The course requirement is counted as tool capabilities, not plugin count. The MVP targets these capabilities through a small plugin set:

| Capability | Module |
| --- | --- |
| Case creation | core/UI |
| Evidence import | core/UI |
| Evidence directory scan | scanner |
| File manifest generation | `hash_manifest` |
| MD5 calculation | `hash_manifest` |
| SHA1 calculation | `hash_manifest` |
| SHA256 calculation | `hash_manifest` |
| File size and timestamp collection | scanner |
| Magic-byte file type detection | `file_type` |
| Extension mismatch detection | `file_type` |
| Keyword search | `keyword_search` |
| Regex search | `keyword_search` |
| Image EXIF extraction | `metadata_extract` |
| PDF metadata extraction | `metadata_extract` |
| Archive index | `archive_index` |
| Timeline generation | artifact/report aggregation |
| Chromium History parsing | `browser_history` bonus |
| Unified artifact review | UI |
| Markdown report export | report generator |

`browser_history` is a bonus feature. If it is not stable by Day 5, it should remain planned or experimental and must not block the main flow.
