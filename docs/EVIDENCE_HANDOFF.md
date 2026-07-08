# Windows Evidence Intake Guide

[中文](EVIDENCE_HANDOFF.zh-CN.md)

`hzltfw` analyzes exported files and directories. It does not directly parse
E01 images, partition tables, or NTFS filesystems in the final coursework
release.

Recommended workflow:

1. Use a forensic tool such as FTK Imager, Autopsy, X-Ways, Arsenal Image
   Mounter, ewf-tools, or The Sleuth Kit to inspect the source image.
2. Export selected Windows files and directories into a normal directory.
3. Use the **Windows export intake** section on the **Evidence** page to inspect
   the exported directory and confirm which recognizable sources are present.
4. Import that exported directory into `hzltfw`.
5. Run the default plugins and export a Markdown report.

## Export Targets

| Target | Example paths | Purpose |
| --- | --- | --- |
| User documents and desktop | `Users\<user>\Documents`, `Users\<user>\Desktop`, `Users\<user>\Downloads` | Documents, archives, downloads, and ordinary user files |
| Chromium profile | `Users\<user>\AppData\Local\Google\Chrome\User Data\Default\History`, `Users\<user>\AppData\Local\Microsoft\Edge\User Data\Default\History` | Input for Hindsight or manual browser review |
| Recent shortcuts | `Users\<user>\AppData\Roaming\Microsoft\Windows\Recent` | Intake checklist source; no built-in LNK parser |
| Registry hives | `Users\<user>\NTUSER.DAT`, `Windows\System32\config\SOFTWARE`, `Windows\System32\config\SYSTEM` | Intake checklist source; review with external tools if needed |
| Windows event logs | `Windows\System32\winevt\Logs\*.evtx` | Intake checklist source; review with external tools if needed |
| Recycle Bin | `$Recycle.Bin` | Intake checklist source for deleted-file context |
| Email and Office files | `*.msg`, `*.docx`, `*.xlsx`, `*.pptx` under user folders | Office metadata is extracted for DOCX; other formats stay as indexed files |

## Course Sample Rules

- Preserve filenames and directory structure when practical.
- Do not commit full evidence samples to this repository.
- Keep sample hashes, expected findings, and intake notes in documentation.
- Use fake personal data for course demonstrations.

The local GUI also has a **Windows export intake** section on the **Evidence**
page. It scans an exported directory, lists recognizable Windows sources, and
shows missing source categories before the same directory is added as evidence.
