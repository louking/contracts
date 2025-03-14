"""event table: add isInvoiceUpdated

Revision ID: 4b35b5d71a46
Revises: 778c5f399640
Create Date: 2025-03-05 12:05:44.203964

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4b35b5d71a46'
down_revision = '778c5f399640'
branch_labels = None
depends_on = None


def upgrade(engine_name):
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name):
    globals()["downgrade_%s" % engine_name]()





def upgrade_():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('event', sa.Column('isInvoiceUpdated', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade_():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('event', 'isInvoiceUpdated')
    # ### end Alembic commands ###

