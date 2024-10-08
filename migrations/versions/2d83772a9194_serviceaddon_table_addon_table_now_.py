"""serviceaddon table; addon table now supports unit pricing

Revision ID: 2d83772a9194
Revises: 61f8c9a58b51
Create Date: 2024-08-23 14:24:09.098645

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2d83772a9194'
down_revision = '61f8c9a58b51'
branch_labels = None
depends_on = None


def upgrade(engine_name):
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name):
    globals()["downgrade_%s" % engine_name]()





def upgrade_():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('serviceaddon',
    sa.Column('service_id', sa.Integer(), nullable=False),
    sa.Column('addon_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['addon_id'], ['addon.id'], ),
    sa.ForeignKeyConstraint(['service_id'], ['service.id'], ),
    sa.PrimaryKeyConstraint('service_id', 'addon_id')
    )
    op.add_column('addon', sa.Column('is_upricing', sa.Boolean(), nullable=True))
    op.add_column('addon', sa.Column('up_basedon', sa.Text(), nullable=True))
    op.add_column('addon', sa.Column('up_subfixed', sa.Integer(), nullable=True))
    # ### end Alembic commands ###

    from sqlalchemy.sql import table, column
    addon = table('addon',
                 column('is_upricing', sa.Boolean))
    op.execute(
        addon.update().\
            values(
                {'is_upricing': op.inline_literal(False)}
            )
    )

def downgrade_():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('addon', 'up_subfixed')
    op.drop_column('addon', 'up_basedon')
    op.drop_column('addon', 'is_upricing')
    op.drop_table('serviceaddon')
    # ### end Alembic commands ###

