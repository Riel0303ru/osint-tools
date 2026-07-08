"""Initial schema

Revision ID: ab1a24ad964e
Revises: 
Create Date: 2026-07-08 13:15:15.675187

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ab1a24ad964e'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if 'scan_results' not in tables:
        op.create_table(
            'scan_results',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('username', sa.Text(), nullable=False),
            sa.Column('platform', sa.Text(), nullable=False),
            sa.Column('status', sa.Text(), nullable=False),
            sa.Column('status_code', sa.Integer(), nullable=True),
            sa.Column('url', sa.Text(), nullable=True),
            sa.Column('confidence', sa.Float(), nullable=True, server_default='1.0'),
            sa.Column('intelligence_score', sa.Float(), nullable=True, server_default='0.0'),
            sa.Column('extra_json', sa.Text(), nullable=True, server_default='{}'),
            sa.Column('scan_timestamp', sa.Text(), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
    else:
        with op.batch_alter_table('scan_results', schema=None) as batch_op:
            batch_op.alter_column('id',
                       existing_type=sa.INTEGER(),
                       nullable=False,
                       autoincrement=True)
            batch_op.alter_column('confidence',
                       existing_type=sa.REAL(),
                       type_=sa.Float(),
                       existing_nullable=True)
            batch_op.alter_column('intelligence_score',
                       existing_type=sa.REAL(),
                       type_=sa.Float(),
                       existing_nullable=True)

    # Create indexes defensively
    existing_indexes = []
    if 'scan_results' in tables:
        existing_indexes = [idx['name'] for idx in inspector.get_indexes('scan_results')]

    if 'ix_scan_results_scan_timestamp' not in existing_indexes:
        op.create_index(op.f('ix_scan_results_scan_timestamp'), 'scan_results', ['scan_timestamp'], unique=False)
    if 'ix_scan_results_username' not in existing_indexes:
        op.create_index(op.f('ix_scan_results_username'), 'scan_results', ['username'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('scan_results')
