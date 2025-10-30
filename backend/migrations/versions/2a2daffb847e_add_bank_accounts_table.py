"""add_bank_accounts_table

Revision ID: 2a2daffb847e
Revises: fb439fa9769c
Create Date: 2025-10-29 20:45:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2a2daffb847e"
down_revision: Union[str, Sequence[str], None] = "fb439fa9769c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "bank_accounts",
        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
            comment="Identificador único"
        ),
        sa.Column(
            "user_id",
            sa.UUID(),
            nullable=False,
            comment="Usuario propietario de la cuenta"
        ),
        sa.Column(
            "name",
            sa.String(length=100),
            nullable=False,
            comment="Nombre visible de la cuenta"
        ),
        sa.Column(
            "color",
            sa.String(length=7),
            nullable=False,
            comment="Color hexadecimal asignado a la cuenta"
        ),
        sa.Column(
            "initial_balance",
            sa.Numeric(precision=15, scale=2),
            nullable=False,
            comment="Saldo inicial registrado al crear la cuenta"
        ),
        sa.Column(
            "current_balance",
            sa.Numeric(precision=15, scale=2),
            nullable=False,
            server_default=sa.text("0"),
            comment="Saldo actual de la cuenta"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Fecha de creación"
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Fecha de última actualización"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "name", name="uq_bank_accounts_user_name"),
        sa.CheckConstraint("initial_balance >= 0", name="ck_bank_accounts_initial_balance_non_negative"),
        sa.CheckConstraint("current_balance >= 0", name="ck_bank_accounts_current_balance_non_negative"),
        comment="Cuentas bancarias administradas por el usuario",
    )
    op.create_index(
        "ix_bank_accounts_user_id",
        "bank_accounts",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_bank_accounts_user_id", table_name="bank_accounts")
    op.drop_table("bank_accounts")
