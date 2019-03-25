"""sponsor, sponsorracedate tables added; client.contactTitle; sponsorbenefit.order

Revision ID: 6ab77bb01462
Revises: e3b4f6259fb3
Create Date: 2019-03-23 14:02:38.484000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '6ab77bb01462'
down_revision = 'e3b4f6259fb3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sponsorracedate',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('race_id', sa.Integer(), nullable=True),
    sa.Column('raceyear', sa.Integer(), nullable=True),
    sa.Column('racedate', sa.String(length=10), nullable=True),
    sa.ForeignKeyConstraint(['race_id'], ['sponsorrace.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('sponsor',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('raceyear', sa.Integer(), nullable=True),
    sa.Column('racecontact', sa.String(length=256), nullable=True),
    sa.Column('amount', sa.Integer(), nullable=True),
    sa.Column('couponcode', sa.String(length=32), nullable=True),
    sa.Column('trend', sa.String(length=32), nullable=True),
    sa.Column('contractDocId', sa.String(length=128), nullable=True),
    sa.Column('race_id', sa.Integer(), nullable=True),
    sa.Column('client_id', sa.Integer(), nullable=True),
    sa.Column('state_id', sa.Integer(), nullable=True),
    sa.Column('level_id', sa.Integer(), nullable=True),
    sa.Column('datesolicited', sa.String(length=10), nullable=True),
    sa.Column('dateagreed', sa.String(length=10), nullable=True),
    sa.Column('invoicesent', sa.String(length=10), nullable=True),
    sa.Column('isRegSiteUpdated', sa.Boolean(), nullable=True),
    sa.Column('isWebsiteUpdated', sa.Boolean(), nullable=True),
    sa.Column('isLogoReceived', sa.Boolean(), nullable=True),
    sa.Column('isSponsorThankedFB', sa.Boolean(), nullable=True),
    sa.Column('notes', sa.String(length=1024), nullable=True),
    sa.ForeignKeyConstraint(['client_id'], ['client.id'], ),
    sa.ForeignKeyConstraint(['level_id'], ['sponsorlevel.id'], ),
    sa.ForeignKeyConstraint(['race_id'], ['sponsorrace.id'], ),
    sa.ForeignKeyConstraint(['state_id'], ['state.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column(u'client', sa.Column('contactTitle', sa.String(length=64), nullable=True))
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
    op.add_column(u'sponsorbenefit', sa.Column('order', sa.Integer(), nullable=True))
    op.alter_column(u'sponsorlevel', 'display',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=True)
    op.add_column(u'sponsorrace', sa.Column('couponproviderid', sa.String(length=128), nullable=True))
    op.add_column(u'sponsorrace', sa.Column('isRDCertified', sa.Boolean(), nullable=True))
    op.add_column(u'sponsorrace', sa.Column('rdemail', sa.String(length=100), nullable=True))
    op.add_column(u'sponsorrace', sa.Column('rdphone', sa.String(length=13), nullable=True))
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
    op.drop_column(u'sponsorrace', 'rdphone')
    op.drop_column(u'sponsorrace', 'rdemail')
    op.drop_column(u'sponsorrace', 'isRDCertified')
    op.drop_column(u'sponsorrace', 'couponproviderid')
    op.alter_column(u'sponsorlevel', 'display',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True)
    op.drop_column(u'sponsorbenefit', 'order')
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
    op.drop_column(u'client', 'contactTitle')
    op.drop_table('sponsor')
    op.drop_table('sponsorracedate')
    # ### end Alembic commands ###
