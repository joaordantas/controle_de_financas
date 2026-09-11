import os
from pathlib import Path


TEST_DB_PATH = Path(__file__).resolve().parents[1] / "storage" / "test_database.db"
os.environ["APP_ENV"] = "test"
os.environ["TEST_DATABASE_URL"] = f"sqlite+pysqlite:///{TEST_DB_PATH.as_posix()}"


def reset_test_database() -> None:
    from database.connection import dispose_engine
    from database.migrations import upgrade_database

    dispose_engine()
    TEST_DB_PATH.unlink(missing_ok=True)
    upgrade_database()


def remove_test_database() -> None:
    from database.connection import dispose_engine

    dispose_engine()
    TEST_DB_PATH.unlink(missing_ok=True)
