"""add course marking lead (#474)

Revision ID: 61f8c9a58b51
Revises: 7ac6ef1d0797
Create Date: 2024-07-26 10:57:25.761106

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '61f8c9a58b51'
down_revision = '7ac6ef1d0797'
branch_labels = None
depends_on = None


def upgrade(engine_name):
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name):
    globals()["downgrade_%s" % engine_name]()





def upgrade_():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('event', sa.Column('markinglead_id', sa.Integer(), nullable=True))
    op.create_foreign_key('event_lead_markinglead_fk1', 'event', 'lead', ['markinglead_id'], ['id'])
    op.add_column('lead', sa.Column('roles', sa.Text(), nullable=True))
    op.add_column('lead', sa.Column('active', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###

    from sqlalchemy.sql import table, column, values
    lead = table('lead',
                 column('roles', sa.Text),
                 column('active', sa.Boolean))
    op.execute(
        lead.update().\
            values(
                {'roles': op.inline_literal('finishline'),
                 'active': op.inline_literal(True)}
            )
    )

def downgrade_():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('lead', 'active')
    op.drop_column('lead', 'roles')
    op.drop_constraint('event_lead_markinglead_fk1', 'event', type_='foreignkey')
    op.drop_column('event', 'markinglead_id')
    # ### end Alembic commands ###

