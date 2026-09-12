"""secure server-side sessions

Revision ID: 7a4c9d2e1f30
Revises: 13ecd0272470
Create Date: 2026-09-11 13:30:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7a4c9d2e1f30"
down_revision: Union[str, None] = "13ecd0272470"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sessoes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("csrf_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "criada_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column("expira_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revogada_em", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash", name="uq_sessoes_token_hash"),
    )
    op.create_index("ix_sessoes_usuario", "sessoes", ["usuario_id"], unique=False)
    op.create_index("ix_sessoes_expiracao", "sessoes", ["expira_em"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_sessoes_expiracao", table_name="sessoes")
    op.drop_index("ix_sessoes_usuario", table_name="sessoes")
    op.drop_table("sessoes")
