from pathlib import Path

from alembic import command
from alembic.config import Config


def get_alembic_config() -> Config:
    root = Path(__file__).resolve().parents[1]
    config = Config(str(root / "alembic.ini"))
    config.set_main_option("script_location", str(root / "migrations"))
    return config


def upgrade_database(revision: str = "head") -> None:
    command.upgrade(get_alembic_config(), revision)
