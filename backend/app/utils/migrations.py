"""Database migration state verification for application startup."""
from __future__ import annotations

from pathlib import Path

from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy.engine import Engine


BACKEND_DIR = Path(__file__).resolve().parents[2]


def migration_heads() -> set[str]:
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "migrations"))
    return set(ScriptDirectory.from_config(config).get_heads())


def database_revisions(engine: Engine) -> set[str]:
    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        return set(context.get_current_heads())


def verify_database_at_head(engine: Engine) -> None:
    expected = migration_heads()
    current = database_revisions(engine)
    if current != expected:
        raise RuntimeError(
            "Database migrations are not current. "
            f"database={sorted(current) or ['<none>']}, expected={sorted(expected)}. "
            "Run 'python -m alembic upgrade head' before starting the API."
        )
