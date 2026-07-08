# Release Notes

[中文](RELEASE_NOTES.zh-CN.md)

## v1.1.0

`v1.1.0` is a stability release for the local NiceGUI application.

### Changes

- Added a narrow compatibility patch for an Engine.IO ASGI disconnect edge case
  that could raise `KeyError: 'REQUEST_METHOD'` during local GUI use.
- Added a regression test that simulates the disconnect event and verifies that
  the patched handler exits without sending a response.
- Kept the v1.0.0 coursework workflow, built-in plugins, external adapters, and
  report export behavior unchanged.

## v1.0.0

`v1.0.0` is the formal coursework delivery release of Hazelita Forensics
Workbench. It is designed for a repeatable local demonstration rather than a
full professional forensic suite.

### Release Scope

- Local NiceGUI workflow for case creation, evidence intake, scanning, plugin
  execution, artifact review, and report export.
- Built-in plugins for hash manifests, file-type mismatch detection, keyword
  and regex hits, archive indexing, and selected metadata extraction.
- Optional external adapters for ALEAPP, iLEAPP, and Hindsight. External tool
  commands are configured in `.hzltfw/config.json`; tool source trees and
  binaries are not vendored into this repository.
- Discovery-oriented artifact UI with typed views for common findings and raw
  JSON kept under an advanced view.
- Chinese/English main UI text with fallback to English for plugin-specific
  details.
- Markdown report export and portable report-bundle export. Report bundles copy
  linked external outputs so they can be submitted or opened on another
  machine.

### Recommended Demo Path

1. Create a case.
2. Add a prepared directory or archive evidence item.
3. Scan the evidence.
4. Review the discovered file index.
5. Run the built-in plugins.
6. Optionally run ALEAPP, iLEAPP, or Hindsight when matching evidence and local
   tool commands are available.
7. Review findings in the discovery center.
8. Export a report bundle for submission or presentation.

### Packaging And Delivery Notes

- Use `uv sync --dev` for development setup.
- Use `uv run hzltfw` for local execution.
- Keep external forensic tools outside the repository and configure their
  commands through `.hzltfw/config.json`.
- Do not commit sample evidence, external tool outputs, or `.hzltfw/` runtime
  workspace data.

### Known Boundaries

- Evidence must be user-exported files, directories, or archives. Raw disk image
  parsing, E01 parsing, partition parsing, and filesystem reconstruction remain
  out of scope for this release.
- External adapters preserve and link external reports instead of importing all
  external findings into the normalized artifact database.
- Archive support is intentionally shallow; ZIP entries are indexed, but archive
  extraction and recursive archive analysis are not release requirements.
- Browser profile analysis is handled through the optional Hindsight external
  adapter; there is no standalone Chromium History parser in this release.
