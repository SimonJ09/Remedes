"""Recreatedeux colonne pour remedes extension cv

Revision ID: 8625fae9b325
Revises: 4f72af6d5f70
Create Date: 2025-01-25 09:38:38.598761

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8625fae9b325'
down_revision = '4f72af6d5f70'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('remedes', schema=None) as batch_op:
        batch_op.create_unique_constraint('unique_nom_partie', ['nom'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('remedes', schema=None) as batch_op:
        batch_op.drop_constraint('unique_nom_partie', type_='unique')

    # ### end Alembic commands ###
