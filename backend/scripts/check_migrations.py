"""Fail when the database is behind or model metadata differs from Alembic."""
from pathlib import Path
import subprocess
import sys


BACKEND_DIR = Path(__file__).resolve().parents[1]


def main() -> int:
    commands = (
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        [sys.executable, "-m", "alembic", "check"],
    )
    for command in commands:
        result = subprocess.run(command, cwd=BACKEND_DIR)
        if result.returncode != 0:
            return result.returncode
    print("Database is at Alembic head and model metadata matches migrations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
