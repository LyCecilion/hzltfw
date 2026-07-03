# Windows Evidence Handoff Guide

[中文](EVIDENCE_HANDOFF.zh-CN.md)

`hzltfw` analyzes exported files and directories. It does not directly parse
E01 images, partition tables, or NTFS filesystems in the MVP workflow.

Recommended workflow:

1. Use a forensic tool such as FTK Imager, Autopsy, X-Ways, Arsenal Image
   Mounter, ewf-tools, or The Sleuth Kit to inspect the source image.
2. Export selected Windows files and directories into a normal directory.
3. Import that exported directory into `hzltfw`.
4. Run the default plugins and export a Markdown report.

## Export Targets

| Target | Example paths | Purpose |
| --- | --- | --- |
| User documents and desktop | `Users\<user>\Documents`, `Users\<user>\Desktop`, `Users\<user>\Downloads` | Documents, archives, downloads, and ordinary user files |
| Chromium profile | `Users\<user>\AppData\Local\Google\Chrome\User Data\Default\History`, `Users\<user>\AppData\Local\Microsoft\Edge\User Data\Default\History` | Optional browser history parsing |
| Recent shortcuts | `Users\<user>\AppData\Roaming\Microsoft\Windows\Recent` | Future LNK parsing |
| Registry hives | `Users\<user>\NTUSER.DAT`, `Windows\System32\config\SOFTWARE`, `Windows\System32\config\SYSTEM` | Future registry quicklook |
| Windows event logs | `Windows\System32\winevt\Logs\*.evtx` | Future EVTX summary |
| Recycle Bin | `$Recycle.Bin` | Future deleted-file review |
| Email and Office files | `*.msg`, `*.docx`, `*.xlsx`, `*.pptx` under user folders | Future email and Office suspicious-content plugins |

## Course Sample Rules

- Preserve filenames and directory structure when practical.
- Do not commit full evidence samples to this repository.
- Keep sample hashes, expected findings, and handoff notes in documentation.
- Use fake personal data for course demonstrations.

The local GUI also has an **Evidence Handoff** page that can export this
checklist as a Markdown file for a specific case or sample.
