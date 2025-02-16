"""Recreatedeux colonne pour remedes

Revision ID: f5c0f080c640
Revises: 1e2f4bede3cd
Create Date: 2025-01-24 19:27:08.573375

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f5c0f080c640'
down_revision = '1e2f4bede3cd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ingredients', schema=None) as batch_op:
        batch_op.drop_column('date_inscription')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ingredients', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date_inscription', sa.DATE(), nullable=True))

    # ### end Alembic commands ###
