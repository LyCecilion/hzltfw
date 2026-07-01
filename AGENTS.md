# AGENTS.md

This repository is the Hazelita Forensics Workbench (`hzltfw`), a course-oriented local digital forensics workbench. AI coding agents must keep the project stable for a short-team deadline and avoid architecture drift.

## Product Scope

- Primary scenario: electronic data forensics course practice and live demonstration.
- MVP flow: create case, add evidence, scan files, run plugins, view artifacts, export Markdown report.
- Required GUI: NiceGUI local web UI.
- Required package workflow: `uv`.
- Windows compatibility is a merge requirement. Fedora/Linux support must not rely on Linux-only behavior.

## Architecture Rules

- Keep the layered structure:
  - `core/`: database, models, workspace, scanner, plugin contracts, runner, report generation.
  - `plugins/`: parser and analyzer implementations.
  - `ui/`: NiceGUI pages/components.
  - `utils/`: small shared helpers.
- Evidence is user-imported input: a directory or a file.
- `evidence_files` are indexed resources found inside an evidence item.
- The core scanner owns directory traversal and path normalization.
- Plugins must not recursively scan the evidence root by themselves.
- Plugins must not write to the database directly.
- Plugins must not import or call NiceGUI.
- Plugins return `ArtifactCreate` objects; the runner persists artifacts and plugin run status.
- A plugin failure must mark only that plugin run as failed. Other selected plugins should continue.

## Data Model Rules

- Use SQLModel for persistence.
- Keep plugin-specific data in `artifacts.data_json`.
- Keep common searchable fields in first-class artifact columns:
  - `artifact_type`
  - `title`
  - `summary`
  - `source_path`
  - `timestamp`
  - `severity`
  - `is_key`
  - `tags_json`
- Do not add plugin-specific tables unless the group has explicitly agreed that JSON artifacts cannot support the workflow.

## Plugin Rules

Plugins implement one of two contracts:

- `EvidencePlugin`: analyzes an evidence item and its indexed files.
- `FilePlugin`: declares `supports(file)` and analyzes matching files.

Every plugin contribution must include:

- Supported inputs and dependencies.
- Artifact types it emits.
- A minimal sample or sample description.
- Expected artifact examples.
- Windows test notes.

Use `PLUGIN_CONTACT.md` as the plugin contract reference.

## Code Style

- Use type hints for public functions and dataclasses.
- Prefer small functions with clear inputs over hidden global state.
- Keep comments sparse and useful.
- Use `pathlib.Path` for filesystem paths.
- Store database timestamps as timezone-aware UTC datetimes.
- Avoid platform-specific path parsing. Use `Path` and stored relative/virtual paths.
- Do not introduce large frameworks or background task systems without agreement.

## Commands

- Install dependencies: `uv sync --dev`
- Run GUI: `uv run hzltfw`
- Run tests: `uv run pytest`
- Lint: `uv run ruff check .`

## Deadline Discipline

- Day 7 is feature freeze.
- Chromium History is a bonus feature. If incomplete by Day 5, leave the interface placeholder and keep the main flow working.
- Do not block the main flow for optional archive recursion, specialized artifact pages, or advanced report styling.

## Git Workflow

- Follow `CONTRIBUTING.md`.
- Never commit directly to `main`.
- Every change must go through a pull request.
- Keep branches short-lived and scoped to one task.
- Do not rewrite another contributor's work to resolve conflicts without review.
- AI-generated code still requires human review and CI.
