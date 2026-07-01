# Contributing

This project uses a lightweight PR-based workflow. Do not push feature work directly to `main`.

## Branch Model

- `main` is the stable integration branch.
- Every change must be made on a short-lived branch and merged through a pull request.
- Keep branches focused. One branch should solve one task or one plugin.
- Delete branches after merge.

Suggested branch names:

```text
core/scanner
core/plugin-runner
ui/artifacts-page
plugin/hash-manifest
plugin/file-type
plugin/keyword-search
docs/git-workflow
fix/windows-paths
```

Use prefixes consistently:

- `core/` for database, scanner, runner, report, and shared architecture.
- `ui/` for NiceGUI pages and components.
- `plugin/` for analysis plugins.
- `docs/` for documentation.
- `fix/` for bug fixes.
- `test/` for test-only work.

## Daily Workflow

1. Start from the latest `main`.

   ```bash
   git switch main
   git pull
   ```

2. Create a branch.

   ```bash
   git switch -c plugin/file-type
   ```

3. Commit small, related changes.

   ```bash
   git status
   git add .
   git commit -m "Add file type plugin skeleton"
   ```

4. Push the branch.

   ```bash
   git push -u origin plugin/file-type
   ```

5. Open a pull request.

6. Wait for CI and review.

7. Merge only after approval from the project lead.

## Pull Request Rules

Every PR must include:

- What changed.
- How to test it.
- Screenshots for visible GUI changes.
- Plugin contract notes for plugin changes.
- Windows test notes if the change touches paths, files, SQLite, or dependencies.

Do not merge a PR if:

- CI fails.
- `uv run ruff check .` fails.
- `uv run pytest` fails.
- The PR bypasses the plugin contract.
- The change writes plugin results directly to the database.
- The change only works on one developer's machine.

## Main Branch Rules

- No direct commits to `main`.
- No force push to `main`.
- No large unreviewed rewrites during the final two days.
- Day 7 is feature freeze. After that, only bug fixes, documentation fixes, sample/report fixes, and demo stabilization should be merged.

## Keeping Branches Updated

Prefer rebasing short-lived branches before opening a PR:

```bash
git switch main
git pull
git switch your-branch
git rebase main
```

If rebase conflicts are confusing, stop and ask the project lead. Do not blindly choose "ours" or "theirs".

For branches already pushed and shared with others, prefer merge instead of rewriting history:

```bash
git switch your-branch
git merge main
```

## Commit Message Style

Use short imperative commit messages:

```text
Add hash manifest plugin
Fix Windows path normalization
Document plugin contract
Render artifact JSON details
```

Avoid vague messages:

```text
update
fix
changes
final
```

## Conflict Rules

- Do not resolve conflicts by deleting another person's work unless the project lead confirms it.
- If a conflict is in `pyproject.toml`, `core/models.py`, `core/plugin.py`, or `PLUGIN_CONTACT.md`, ask for review before merging.
- If two plugins need the same helper, put the helper under `src/hzltfw/utils/` or ask before duplicating logic.

## AI Coding Rules

AI-generated changes still need PR review.

When using AI coding tools:

- Point the tool to `AGENTS.md`, `ARCHITECTURE.md`, and `PLUGIN_CONTACT.md`.
- Ask it to keep changes scoped to the branch task.
- Review generated code before committing.
- Run checks before opening the PR.
- Do not let AI rewrite unrelated files.

## Useful Commands

```bash
uv sync --dev
uv run hzltfw
uv run ruff check .
uv run pytest
git status
git diff
```
