"""sponsorracedate .beneficiary, .raceloc; sponsorracevbl table

Revision ID: 7ad03847e5db
Revises: 6ab77bb01462
Create Date: 2019-04-03 07:30:38.004000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '7ad03847e5db'
down_revision = '6ab77bb01462'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sponsorracevbl',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('variable', sa.String(length=32), nullable=True),
    sa.Column('value', sa.String(length=128), nullable=True),
    sa.Column('race_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['race_id'], ['sponsorrace.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.alter_column(u'course', 'isStandard',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=True)
    op.alter_column(u'event', 'isOnCalendar',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=True)
    op.alter_column(u'service', 'isCalendarBlocked',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=True)
    op.alter_column(u'sponsor', 'isLogoReceived',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=True)
    op.alter_column(u'sponsor', 'isRegSiteUpdated',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=True)
    op.alter_column(u'sponsor', 'isSponsorThankedFB',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=True)
    op.alter_column(u'sponsor', 'isWebsiteUpdated',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=True)
    op.add_column(u'sponsorbenefit', sa.Column('race_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'sponsorbenefit', 'sponsorrace', ['race_id'], ['id'])
    op.alter_column(u'sponsorlevel', 'display',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=True)
    op.alter_column(u'sponsorrace', 'isRDCertified',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=True)
    op.add_column(u'sponsorracedate', sa.Column('beneficiary', sa.String(length=128), nullable=True))
    op.add_column(u'sponsorracedate', sa.Column('raceloc', sa.String(length=128), nullable=True))
    op.alter_column(u'tag', 'isBuiltIn',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=True)
    op.alter_column(u'user', 'active',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(u'user', 'active',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True)
    op.alter_column(u'tag', 'isBuiltIn',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True)
    op.drop_column(u'sponsorracedate', 'raceloc')
    op.drop_column(u'sponsorracedate', 'beneficiary')
    op.alter_column(u'sponsorrace', 'isRDCertified',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True)
    op.alter_column(u'sponsorlevel', 'display',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True)
    op.drop_constraint(None, 'sponsorbenefit', type_='foreignkey')
    op.drop_column(u'sponsorbenefit', 'race_id')
    op.alter_column(u'sponsor', 'isWebsiteUpdated',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True)
    op.alter_column(u'sponsor', 'isSponsorThankedFB',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True)
    op.alter_column(u'sponsor', 'isRegSiteUpdated',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True)
    op.alter_column(u'sponsor', 'isLogoReceived',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True)
    op.alter_column(u'service', 'isCalendarBlocked',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True)
    op.alter_column(u'event', 'isOnCalendar',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True)
    op.alter_column(u'course', 'isStandard',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True)
    op.drop_table('sponsorracevbl')
    # ### end Alembic commands ###
