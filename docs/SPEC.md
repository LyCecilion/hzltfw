# Hazelita Forensics Workbench Final Specification

## Goal

`hzltfw` serves an electronic data forensics course practice scenario. The final
coursework release is a local, repeatable demonstration workbench, not a full
professional forensic suite.

## Demonstration Story

A prepared sample contains ordinary user files, downloaded archives, suspicious
renamed files, metadata-bearing documents or images, and optional exported
mobile/browser artifacts for external tools. The workbench imports the sample,
scans files, runs analysis plugins, presents normalized artifacts, and exports a
Markdown report or portable report bundle.

## Supported Flow

1. Create, list, and delete cases.
2. Add file or directory evidence by path.
3. Scan evidence into normalized `evidence_files`.
4. Optionally inspect an exported Windows directory before adding it.
5. Run the default built-in plugins.
6. Optionally run configured ALEAPP, iLEAPP, or Hindsight external adapters.
7. Persist plugin runs and artifacts.
8. Review artifacts in the local NiceGUI interface.
9. Export a Markdown report or report bundle.

## Built-In Plugins And Support Modules

| Component | Purpose | Final status |
| --- | --- | --- |
| `hash_manifest` | MD5/SHA1/SHA256 file manifest for indexed physical files | Implemented |
| `file_type` | Magic-byte extension mismatch warnings | Implemented |
| `keyword_search` | Built-in demo regex hits for text-like files | Implemented |
| `archive_index` | ZIP index and suspicious archive entry-name review | Implemented |
| `metadata_extract` | Image EXIF, PDF metadata, and DOCX core properties | Implemented |
| `external_forensics` | Manual ALEAPP, iLEAPP, and Hindsight adapter runs | Implemented optional feature |
| `handoff` | Exported Windows directory inspection from the Evidence page | Implemented support feature |
| `report` | Markdown report, timeline aggregation, optional manifest, and report bundle | Implemented |

There is no standalone Chromium History parser in the final release. Browser
profile analysis is handled through the optional Hindsight external adapter.

## Capability Matrix

| Capability | Implementation |
| --- | --- |
| Case creation, listing, and deletion | `cases` table and GUI |
| Evidence import, scan, and deletion | `evidence_items`, `evidence_files`, scanner, and GUI |
| File size and timestamp collection | scanner |
| MD5/SHA1/SHA256 calculation | `hash_manifest` |
| File manifest generation | `hash_manifest` |
| Magic-byte file type detection | `file_type` |
| Extension mismatch warning | `file_type` |
| Keyword and regex search | `keyword_search` |
| Image EXIF metadata | `metadata_extract` |
| PDF metadata | `metadata_extract` |
| DOCX metadata | `metadata_extract` |
| ZIP archive listing | `archive_index` |
| Suspicious ZIP entry-name hints | `archive_index` |
| Exported Windows evidence intake | `handoff` core and Evidence page |
| Artifact review and filtering | Artifacts GUI page |
| Timeline generation | Report aggregation over timestamped artifacts |
| Markdown report export | report generator |
| Portable report bundle export | report generator |
| ALEAPP/iLEAPP/Hindsight external reports | `external_forensics` |

## Boundaries

- Evidence must be user-exported files, directories, or archives.
- Raw disk image parsing, E01 parsing, partition parsing, and filesystem
  reconstruction are out of scope.
- Archive support is intentionally shallow. ZIP entries are indexed, but
  archives are not extracted or recursively analyzed.
- External adapters preserve and link external reports instead of importing all
  external findings into the normalized artifact database.
- Full file manifests in reports are optional because they can be large.

## Sample Evidence Policy

The full sample evidence should not be committed to the repository. Store the
sample externally and keep only lightweight notes in the repo:

- sample download or handoff instructions
- SHA256 of the sample archive when applicable
- expected directory structure
- expected findings
- keywords used in the demonstration

The sample must not contain real personal privacy data.
