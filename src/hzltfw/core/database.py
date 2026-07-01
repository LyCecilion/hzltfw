from collections.abc import Iterator
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine

DEFAULT_DB_PATH = Path(".hzltfw") / "hzltfw.db"


def sqlite_url(path: str | Path = DEFAULT_DB_PATH) -> str:
    db_path = Path(path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_path}"


def create_db_engine(db_url: str | None = None):
    url = db_url or sqlite_url()
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args)


def init_db(engine) -> None:
    SQLModel.metadata.create_all(engine)


def session_scope(engine) -> Iterator[Session]:
    with Session(engine) as session:
        yield session
