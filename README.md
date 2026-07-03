# Hazelita Forensics Workbench

[中文](README.zh-CN.md)

`hzltfw` is a local digital forensics workbench for electronic data forensics course practice. The first deliverable focuses on a stable live-demonstration flow: create a case, add a prepared Windows-style evidence sample, run analysis plugins, inspect artifacts in a GUI, and export a Markdown report.

## Usage

### Start The Workbench

Install the project dependencies and start the local GUI:

```bash
uv sync
uv run hzltfw
```

By default the web UI binds to `127.0.0.1:8080`. To use another address:

```bash
uv run hzltfw --host 127.0.0.1 --port 8081
```

Runtime data is written under `.hzltfw/` in the current working directory:

- `.hzltfw/hzltfw.db`: local SQLite database.
- `.hzltfw/workspace/`: copied evidence metadata, plugin outputs, and external
  tool outputs.
- `.hzltfw/config.json`: language and external tool command configuration.

Do not commit `.hzltfw/`, sample evidence, or generated reports unless a course
submission explicitly asks for exported report artifacts.

### Analyze Evidence

1. Open the local UI.
2. Create a case from the **Cases** page.
3. Add file, directory, or archive evidence from the **Evidence** page.
4. Scan the evidence so `hzltfw` can index files into `evidence_files`.
5. Run selected built-in plugins from the **Analysis** page.
6. Review findings in the discovery/artifacts page.
7. Export a Markdown report or a portable report bundle from the **Reports**
   page.

For Windows image or E01 coursework, first export the target files with a
dedicated forensic tool, then import the exported directory into `hzltfw`. See
[docs/EVIDENCE_HANDOFF.md](docs/EVIDENCE_HANDOFF.md).

### Configure External Tools

`hzltfw` can call locally installed ALEAPP, iLEAPP, and Hindsight adapters. The
external tools are not installed, vendored, or committed by this repository.
Configure them either from the **Analysis** page command configuration panel or
by editing `.hzltfw/config.json`.

Supported adapters:

| Tool | Best input | Notes |
| --- | --- | --- |
| ALEAPP | Android filesystem export or archive | Use `fs`, `zip`, `tar`, or `gz` input type. |
| iLEAPP | iOS/iPadOS filesystem, iTunes backup, or archive | Use `fs`, `zip`, `tar`, `gz`, `itunes`, or `file` input type. |
| Hindsight | Browser profile directory | Prefer the full Chrome/Edge/Chromium profile directory, not only `History`. |

Example `.hzltfw/config.json`:

```json
{
  "language": "zh-CN",
  "external_tools": {
    "aleapp": {
      "name": "aleapp",
      "command": ["python", "/path/to/ALEAPP/aleapp.py"],
      "enabled": true
    },
    "ileapp": {
      "name": "ileapp",
      "command": ["/path/to/ileapp"],
      "enabled": true
    },
    "hindsight": {
      "name": "hindsight",
      "command": ["python", "/path/to/hindsight.py"],
      "enabled": true
    }
  }
}
```

Each `command` must be a JSON string array. Do not use shell aliases, pipes,
redirection, environment variable expansion, or platform-specific shell syntax;
the app runs commands with `shell=False` for Windows/Linux portability.

Recommended command examples:

```json
["C:\\Tools\\ALEAPP\\.venv\\Scripts\\python.exe", "C:\\Tools\\ALEAPP\\aleapp.py"]
["C:\\Tools\\iLEAPP\\iLEAPP.exe"]
["C:\\Tools\\hindsight\\.venv\\Scripts\\python.exe", "C:\\Tools\\hindsight\\hindsight.py"]
```

```json
["/opt/ALEAPP/.venv/bin/python", "/opt/ALEAPP/aleapp.py"]
["/opt/iLEAPP/iLEAPP.AppImage"]
["/opt/hindsight/.venv/bin/python", "/opt/hindsight/hindsight.py"]
```

For source-checkout tools, prefer that tool's own virtual environment Python
instead of reusing the `hzltfw` environment. This keeps ALEAPP, iLEAPP, and
Hindsight dependency conflicts isolated.

To run an external analysis:

1. Add and scan the evidence item.
2. Open the **Analysis** page.
3. Check the external tool health status. Health checks run the configured
   command with `--help`.
4. Use evidence probing as a hint, then choose the tool and input type yourself.
5. Start the external run and wait for it to finish.
6. Open the generated `external.report` artifact or export a report bundle.

External tool runs write output to:

```text
.hzltfw/workspace/case-<case-id>/external_runs/<tool>/run-<plugin-run-id>/
```

Use **Report bundle** export when external tools are involved. The bundle copies
external HTML/JSONL/XLSX outputs and links them from `report.md`, making the
submission portable. More details are in
[docs/EXTERNAL_TOOLS.md](docs/EXTERNAL_TOOLS.md).

## Deployment And Development

### Requirements

- Python 3.12+
- uv
- Git
- Optional: Nix with flakes support

The application stack is Python, NiceGUI, SQLite, SQLModel, ruff, and pytest.

### Linux

```bash
git clone <repo-url>
cd hzltfw
uv sync --dev
uv run hzltfw
```

For a release archive instead of a Git checkout, extract the archive, enter the
project directory, then run the same `uv sync --dev` and `uv run hzltfw`
commands.

If you use Nix:

```bash
nix develop
uv sync --dev
uv run hzltfw
```

Linux external tools can be configured as Python source checkouts, standalone
executables, or AppImage binaries. If an AppImage cannot run because FUSE is not
available on the target machine, extract it or use another binary/source
deployment supported by that external tool.

### Windows

Install Python 3.12+, Git, and uv, then run:

```powershell
git clone <repo-url>
cd hzltfw
uv sync --dev
uv run hzltfw
```

For a release archive, unzip it, open PowerShell in the project directory, then
run the same `uv sync --dev` and `uv run hzltfw` commands.

Use Windows paths in `.hzltfw/config.json` and escape backslashes in JSON:

```json
["C:\\Tools\\ALEAPP\\.venv\\Scripts\\python.exe", "C:\\Tools\\ALEAPP\\aleapp.py"]
```

Prefer per-tool virtual environments for source versions of ALEAPP, iLEAPP, and
Hindsight. If a tool provides a Windows executable, point the command directly
at the executable.

### Developer Checks

Run these before opening a PR or cutting a release:

```bash
uv run ruff check .
uv run pytest
```

## Release

Current release: `v1.0.0`.

This is the first formal coursework release. It keeps the local NiceGUI
workflow, built-in artifact plugins, optional ALEAPP/iLEAPP/Hindsight adapters,
Chinese/English UI text, and portable report-bundle export in one packageable
desktop-friendly app. See [docs/RELEASE_NOTES.md](docs/RELEASE_NOTES.md) for
the release scope, demo path, and known boundaries.

## Collaboration

All feature work goes through pull requests. Do not push directly to `main`.
See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for the lightweight Git workflow,
branch naming rules, PR checklist, and AI coding rules.

Plugin work should follow [docs/PLUGIN_CONTACT.md](docs/PLUGIN_CONTACT.md) and
[docs/PLUGIN_TASKS.md](docs/PLUGIN_TASKS.md).
For Windows image or E01-based coursework, export selected files first and use
[docs/EVIDENCE_HANDOFF.md](docs/EVIDENCE_HANDOFF.md) to inspect the exported
directory.
For ALEAPP, iLEAPP, Hindsight, and report-bundle workflows, see
[docs/EXTERNAL_TOOLS.md](docs/EXTERNAL_TOOLS.md).

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
| DOCX metadata extraction | `metadata_extract` |
| Archive index | `archive_index` |
| Exported Windows evidence intake | evidence UI/core |
| Timeline generation | artifact/report aggregation |
| Chromium History parsing | `browser_history` bonus |
| Unified artifact review | UI |
| Markdown report export | report generator |
| External ALEAPP/iLEAPP/Hindsight adapters | `external_forensics` |
| Portable report bundle export | report generator |

`browser_history` is a bonus feature. If it is not stable by Day 5, it should remain planned or experimental and must not block the main flow.
