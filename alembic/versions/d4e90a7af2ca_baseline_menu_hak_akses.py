"""baseline menu & hak_akses

Revision ID: d4e90a7af2ca
Revises: 11abeaef6cea
Create Date: 2025-09-18 18:22:59.489090

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e90a7af2ca'
down_revision: Union[str, Sequence[str], None] = '11abeaef6cea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
