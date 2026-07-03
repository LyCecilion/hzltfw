# Hazelita Forensics Workbench Specification

## Goal

`hzltfw` serves an electronic data forensics course practice scenario. It is not trying to be a full professional forensic suite in the first release. The first release must support a repeatable live demonstration over a prepared Windows-style evidence sample.

## MVP Demonstration Story

A student is suspected of leaking course material. The prepared evidence sample contains ordinary files, downloaded archives, suspicious renamed files, metadata-bearing documents or images, and optionally a Chromium `History` database. The workbench imports the sample, runs analysis plugins, presents normalized artifacts, and exports a Markdown report.

## Must-Have Flow

1. Create a case.
2. Add evidence from a file or directory path.
3. Scan evidence into normalized `evidence_files`.
4. Run analysis plugins.
5. Persist plugin runs and artifacts.
6. Review artifacts in a local GUI.
7. Export a Markdown report.

## Required Plugins

| Plugin | Purpose | MVP Status |
| --- | --- | --- |
| `hash_manifest` | MD5/SHA1/SHA256 and file manifest | Implemented |
| `file_type` | Magic-byte extension mismatch warnings | Implemented |
| `keyword_search` | Built-in demo regex hits | Implemented |
| `archive_index` | ZIP index and suspicious archive entry review | Implemented |
| `metadata_extract` | Image EXIF, PDF metadata, and DOCX core properties | Implemented |
| `handoff` | Inspect exported Windows evidence directories from Evidence page | Implemented support feature |
| `timeline` | Time-based artifact/report aggregation | Implemented through report aggregation |
| `browser_history` | Chromium History parsing | Bonus/planned |

`timeline` may be implemented as artifact/report aggregation rather than a standalone plugin.

## Capability Matrix

| Capability | Implementation |
| --- | --- |
| Case creation | `cases` table and GUI |
| Evidence import | `evidence_items` table and GUI |
| Evidence scan | `evidence_files` scanner |
| File manifest | `hash_manifest` |
| MD5/SHA1/SHA256 | `hash_manifest` |
| File size and timestamps | scanner |
| File type identification | `file_type` |
| Extension mismatch warning | `file_type` |
| Keyword search | `keyword_search` |
| Regex search | `keyword_search` |
| Image EXIF metadata | `metadata_extract` |
| PDF metadata | `metadata_extract` |
| DOCX metadata | `metadata_extract` |
| Archive listing | `archive_index` |
| Exported Windows evidence intake | `handoff` core, evidence UI |
| Artifact review | artifacts GUI page |
| Timeline generation | report/UI artifact aggregation |
| Markdown report export | report generator |
| Chromium History | `browser_history`, bonus |

## Degradation Rules

- Day 7 is feature freeze.
- If `browser_history` is incomplete by the end of Day 5, remove it from the live demo path and keep it as planned or experimental.
- Archive recursion and extraction are not required for MVP. The current version indexes ZIP entries only.
- Full file manifest in reports is optional and controlled by an export option.
- E01, partition, and filesystem parsing are out of scope for the MVP. Export files with a dedicated forensic tool first, then inspect/import the exported directory.

## Sample Evidence Policy

The full sample evidence should not be committed to the repository. Store the sample externally and keep these files in the repo:

- sample download or handoff instructions
- SHA256 of the sample archive
- expected directory structure
- expected findings
- keywords used in the demonstration

The sample must not contain real personal privacy data.
