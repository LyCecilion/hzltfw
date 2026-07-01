import argparse
from pathlib import Path

from hzltfw.app import run_app


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="hzltfw",
        description="Hazelita Forensics Workbench",
    )
    parser.add_argument(
        "--db",
        default=str(Path(".hzltfw") / "hzltfw.db"),
        help="SQLite database path.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="GUI bind host.")
    parser.add_argument("--port", default=8080, type=int, help="GUI bind port.")
    args = parser.parse_args()

    run_app(db_path=args.db, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
