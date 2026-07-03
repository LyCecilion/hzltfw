# External Tools

[中文](EXTERNAL_TOOLS.zh-CN.md)

`hzltfw` can call locally installed external forensic tools and keep their
outputs inside the case workspace. The external tools themselves are not
vendored, committed, or installed by this repository.

## Supported Adapters

| Tool | Purpose | Input |
| --- | --- | --- |
| ALEAPP | Android extraction analysis | `fs`, `zip`, `tar`, `gz` |
| iLEAPP | iOS/iPadOS extraction analysis | `fs`, `zip`, `tar`, `gz`, `itunes`, `file` |
| Hindsight | Chromium/Firefox browser artifact analysis | browser profile directory |

The Analysis page can probe an evidence path before running a tool. The probe
only inspects directory paths or archive member names and suggests likely tools;
the operator still chooses the tool and input type.

## Configuration

External tool commands are stored in `.hzltfw/config.json`.

Example:

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

Use a JSON string array for each command. Do not use shell-specific syntax,
pipes, aliases, or environment variable expansion. This keeps the adapter
portable across Windows and Linux.

Windows examples:

```json
["py", "-3", "C:\\Tools\\ALEAPP\\aleapp.py"]
["C:\\Tools\\ileapp.exe"]
```

Linux examples:

```json
["python3", "/opt/ALEAPP/aleapp.py"]
["/opt/ileapp"]
```

## Output and Report Bundles

Each run writes under:

```text
.hzltfw/workspace/case-<case-id>/external_runs/<tool>/run-<plugin-run-id>/
```

Plugins emit normalized `external.report` artifacts with the output directory,
report entry file, command, stdout, and stderr summary.

The Reports page has two export modes:

- Markdown: writes one Markdown file.
- Report bundle: writes `report.md` plus `external/<tool>/<run-id>/...`.

Use report bundles for coursework submission because external HTML/JSONL/XLSX
outputs are copied with relative links.

## Cross-Platform Notes

- `hzltfw` does not install external tools.
- Health checks show whether the configured command can run `--help`.
- Commands are executed with `subprocess.run(..., shell=False)`.
- Paths are handled with `pathlib`.
- Hindsight should receive a browser profile directory, not just a single
  `History` SQLite file.
