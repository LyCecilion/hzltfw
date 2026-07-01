from pathlib import Path


def default_workspace_path() -> Path:
    path = Path(".hzltfw") / "workspace"
    path.mkdir(parents=True, exist_ok=True)
    return path


def case_workspace_path(case_id: int, root: Path | None = None) -> Path:
    workspace_root = root or default_workspace_path()
    path = workspace_root / f"case-{case_id}"
    path.mkdir(parents=True, exist_ok=True)
    return path
