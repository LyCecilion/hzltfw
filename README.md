<!-- markdownlint-disable MD033 MD036 MD041 -->

<div align="center">

![hzltfw banner](./assets/banner.png)

# Hazelita Forensics Workbench

A local forensics workbench for electronic data forensics coursework

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Cascadia+Code&size=15&duration=3000&pause=500&color=2C81F7&center=true&vCenter=true&multiline=true&width=480&height=90&lines=From+the+sea+of+bits%2C+salvage+the+echoes+of+memory%2C;and+let+every+forgotten+byte+retell+the+truth;this+is+the+compass+woven+of+mistlight%2C;guiding+to+the+shore+named+%E2%80%98Veritas%E2%80%99.)](https://git.io/typing-svg)

[中文](README.zh-CN.md) / [Site](https://hzltfw.stellalyr.ink)

</div>

> [!WARNING]
> The coursework development cycle for this project has ended.<br/>
> To keep `hzltfw` lightweight and portable, this repository no longer develops new features or accepts feature PRs.

## 📖 About

`hzltfw` is a local forensics workbench built for an electronic data forensics course.

It is not a full commercial forensic suite. It provides a repeatable local demonstration loop: create a case, add prepared evidence, scan files, run analysis plugins, review artifacts in the GUI, and export a Markdown report or portable report bundle.

## ✨ Features

The final coursework release includes:

- Local NiceGUI workflow for cases, evidence, analysis, discoveries, and reports.
- File, directory, or archive path intake with indexed records in `evidence_files`.
- Windows export directory inspection before import, covering common user folders, browser profiles, registry hives, event logs, recycle-bin paths, and related source categories.
- Default built-in plugins for hash manifests, file-type mismatch warnings, keyword/regex hits, ZIP archive indexing, and image/PDF/DOCX metadata extraction.
- External tool adapters for locally configured ALEAPP, iLEAPP, and Hindsight runs, with outputs stored in the case workspace and normalized artifacts returned to the app.
- Discovery review with filters by artifact type, severity, plugin, and key findings, plus raw JSON details.
- Single-file Markdown report export and portable report-bundle export with copied external tool outputs.
- Python 3.12+, SQLite, SQLModel, and `uv` tooling for local Windows and Linux use.

Course samples should be prepared by the user or exported from source images. They should not be committed to this repository.

## 👀 Preview

![Demo discoveries](./assets/demo.png)

## 🚀 Quick Start

### Start `hzltfw`

Make sure `uv` is installed. Clone this repository, install dependencies, and start the local GUI:

```bash
uv sync
uv run hzltfw
```

By default, the web UI binds to `127.0.0.1:8080`. To use another port:

```bash
uv run hzltfw --host 127.0.0.1 --port 8081
```

Runtime data is written under `.hzltfw/` in the current working directory:

- `.hzltfw/hzltfw.db`: local SQLite database.
- `.hzltfw/workspace/`: evidence metadata, plugin outputs, and external tool outputs.
- `.hzltfw/config.json`: language and external tool command configuration.

Do not commit `.hzltfw/`, sample evidence, or generated reports unless a course submission explicitly asks for exported report artifacts.

## 📝 Usage

1. Open the local UI.
2. Create a case from the **Cases** page.
3. Add file, directory, or archive evidence from the **Evidence** page.
4. Scan the evidence so files are indexed into `evidence_files`.
5. Run the default built-in plugins from the **Analysis** page.
6. When needed, configure and run ALEAPP, iLEAPP, or Hindsight from the **Analysis** page.
7. Filter and review findings in the discoveries / artifacts page.
8. Export a Markdown report or portable report bundle from the **Reports** page.

For evidence samples from Windows images or E01 files, first export the target files with a dedicated forensic tool, then import the exported directory into `hzltfw`. See [docs/EVIDENCE_HANDOFF.md](docs/EVIDENCE_HANDOFF.md).

## ⚙️ Configuration

`hzltfw` can call locally installed ALEAPP, iLEAPP, and Hindsight adapters. The external tools are not installed, vendored, or committed by this repository. Configure them from the command configuration panel on the **Analysis** page, or edit `.hzltfw/config.json` directly.

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

Each `command` must be a JSON string array. Do not use shell aliases, pipes, redirection, environment variable expansion, or platform-specific shell syntax; the app runs commands with `shell=False` for Windows/Linux portability.

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

For source-checkout tools, prefer that tool's own virtual environment Python instead of reusing the `hzltfw` Python environment. This isolates ALEAPP, iLEAPP, and Hindsight dependency conflicts.

To run an external analysis:

1. Add and scan the evidence item.
2. Open the **Analysis** page.
3. Check the external tool health status. Health checks run the configured command with `--help`.
4. Use evidence probing as a hint, then choose the tool and input type yourself.
5. Start the external tool run and wait for it to finish.
6. Open the generated `external.report` artifact or export a report bundle.

External tool runs write output to:

```text
.hzltfw/workspace/case-<case-id>/external_runs/<tool>/run-<plugin-run-id>/
```

Use **Report bundle** export when external tools are involved. The bundle copies external HTML/JSONL/XLSX outputs and links them from `report.md`, making the submission portable. More details are in [docs/EXTERNAL_TOOLS.md](docs/EXTERNAL_TOOLS.md).

## 📁 Project Architecture

```text
src/hzltfw/
  core/      database, models, scanner, plugin contracts, runner, reports, and external tool wrappers
  plugins/   built-in analysis plugins and external tool adapters
  ui/        NiceGUI pages, artifact views, and local interactions
  utils/     small shared helpers for hashing, timestamps, and i18n
```

Core data flow:

1. `EvidenceItem` records a user-added file or directory evidence item.
2. The core scanner walks the evidence and creates `EvidenceFile` indexes.
3. The runner creates a `PluginRun` for each plugin and passes the `EvidenceItem` plus indexed files to the plugin.
4. Plugins return `ArtifactCreate` only. They do not write to the database or call NiceGUI.
5. The runner persists `Artifact` records. The UI and report generator read common artifact fields and `data_json`.

For more detail, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## ✅ Final Capability List

| Capability | Implementation |
| --- | --- |
| Case creation, listing, and deletion | `core/models.py`, `ui/pages/cases.py` |
| File/directory evidence add, scan, and deletion | `core/scanner.py`, `ui/pages/evidence.py` |
| Windows export directory inspection | `core/handoff.py`, `ui/pages/evidence.py` |
| MD5/SHA1/SHA256 file manifest | `plugins/hash_manifest.py` |
| Magic-byte extension mismatch detection | `plugins/file_type.py` |
| Email, phone, student-ID, and demo regex hits | `plugins/keyword_search.py` |
| ZIP entry indexing and suspicious entry-name hints | `plugins/archive_index.py` |
| Image EXIF, PDF metadata, and DOCX core properties | `plugins/metadata_extract.py` |
| ALEAPP/iLEAPP/Hindsight external report adapters | `plugins/external_forensics.py` |
| Artifact filters, typed detail views, and raw JSON review | `ui/pages/artifacts.py`, `ui/artifact_views.py` |
| Markdown report and report-bundle export | `core/report.py`, `ui/pages/reports.py` |

Explicitly unsupported: direct E01/raw disk image parsing, partition-table parsing, NTFS filesystem reconstruction, recursive archive extraction, and full import of every external tool finding.

## 💻 Development

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

For a release archive instead of a Git checkout, extract the archive, enter the project directory, then run the same `uv sync --dev` and `uv run hzltfw` commands.

If you use Nix:

```bash
nix develop
uv sync --dev
uv run hzltfw
```

Linux external tools can be configured as Python source checkouts, standalone executables, or AppImage binaries. If an AppImage cannot run because FUSE is not available on the target machine, extract it or use another binary/source deployment supported by that external tool.

### Windows

Install Python 3.12+, Git, and uv, then run:

```powershell
git clone <repo-url>
cd hzltfw
uv sync --dev
uv run hzltfw
```

For a release archive, unzip it, open PowerShell in the project directory, then run the same `uv sync --dev` and `uv run hzltfw` commands.

Use Windows paths in `.hzltfw/config.json` and escape backslashes in JSON:

```json
["C:\\Tools\\ALEAPP\\.venv\\Scripts\\python.exe", "C:\\Tools\\ALEAPP\\aleapp.py"]
```

Prefer per-tool virtual environments for source versions of ALEAPP, iLEAPP, and Hindsight. If a tool provides a Windows executable, point the command directly at the executable.

### Developer Checks

Run these before maintenance fixes or releases:

```bash
uv run ruff check .
uv run pytest
```

## 🚢 Release

Current release: `v1.1.0`.

See [docs/RELEASE_NOTES.md](docs/RELEASE_NOTES.md) for the release scope, demo path, and known boundaries.

## 🤝 Contributing

This project no longer accepts feature PRs. After coursework delivery, the repository only keeps room for maintenance fixes, documentation corrections, and release cleanup.

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for the lightweight Git workflow, PR checklist, and AI coding rules. See [docs/PLUGIN_CONTACT.md](docs/PLUGIN_CONTACT.md) and [docs/PLUGIN_TASKS.md](docs/PLUGIN_TASKS.md) for the plugin interface and final built-in plugin notes.

## 🙏 Acknowledgements

Thanks to the hzltForens!cs and Project Hazelita communities for supporting `hzltfw`.

## 📄 License

[MIT LICENSE](./LICENSE)
