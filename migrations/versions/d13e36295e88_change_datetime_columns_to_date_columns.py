"""Change datetime columns to date columns

Revision ID: d13e36295e88
Revises: 7561271c76fd
Create Date: 2025-07-25 11:02:23.925805

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd13e36295e88'
down_revision = '7561271c76fd'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('task', sa.Column('due_on_date', sa.Date()))
    op.add_column('task', sa.Column('created_on_date', sa.Date()))

    op.execute('''
        UPDATE task
        SET due_on_date = DATE(due_date),
            created_on_date = DATE(created_on)
        WHERE created_on IS NOT NULL OR due_date IS NOT NULL
    ''')

    op.drop_column('task', 'created_on')
    op.drop_column('task', 'due_date')

    op.alter_column('task', 'created_on_date', new_column_name='created_on')
    op.alter_column('task', 'due_on_date', new_column_name='due_on')


def downgrade():
    op.add_column('task', sa.Column('due_on_datetime', sa.DateTime()))
    op.add_column('task', sa.Column('created_on_datetime', sa.DateTime()))

    op.execute('''
        UPDATE task
        SET due_on_datetime = datetime(due_on),
            created_on_datetime = datetime(created_on)
        WHERE due_on IS NOT NULL OR created_on IS NOT NULL
    ''')

    op.drop_column('task', 'due_on')
    op.drop_column('task', 'created_on')

    op.alter_column('task', 'due_on_datetime', new_column_name='due_date')
    op.alter_column('task', 'created_on_datetime', new_column_name='created_on')
