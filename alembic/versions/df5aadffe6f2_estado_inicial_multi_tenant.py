"""estado inicial multi-tenant

Revision ID: df5aadffe6f2
Revises:
Create Date: 2026-06-07 20:32:31.178741

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df5aadffe6f2'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    columnas = [c['name'] for c in inspector.get_columns('requerimientos')]
    if 'proyecto_id' not in columnas:
        op.add_column('requerimientos', sa.Column('proyecto_id', sa.Integer(), nullable=True))

    fks = [fk.get('referred_table') for fk in inspector.get_foreign_keys('requerimientos')]
    if 'proyectos' not in fks:
        op.create_foreign_key(None, 'requerimientos', 'proyectos', ['proyecto_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint(None, 'requerimientos', type_='foreignkey')
    op.drop_column('requerimientos', 'proyecto_id')
