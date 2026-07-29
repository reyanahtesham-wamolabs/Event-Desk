"""Ticket Tiers

Revision ID: 00d931d7bcee
Revises: 9f380ad7a547
Create Date: 2026-07-29 19:20:43.787527

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '00d931d7bcee'
down_revision: Union[str, Sequence[str], None] = '9f380ad7a547'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Create the enum type first
    ticket_tier = sa.Enum("GOLD", "SILVER", "BRONZE", name="tickettier")
    ticket_tier.create(op.get_bind(), checkfirst=True)

    # Then add the column using that enum
    op.add_column(
        "tickets",
        sa.Column("ticket_tier", ticket_tier, nullable=False),
    )

def downgrade() -> None:
    op.drop_column("tickets", "ticket_tier")

    ticket_tier = sa.Enum("GOLD", "SILVER", "BRONZE", name="tickettier")
    ticket_tier.drop(op.get_bind(), checkfirst=True)
