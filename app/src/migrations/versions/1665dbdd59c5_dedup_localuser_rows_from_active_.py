"""dedup localuser rows from active-filter bug (loutilities#103)

Revision ID: 1665dbdd59c5
Revises: 9b95b190721e
Create Date: 2026-08-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '1665dbdd59c5'
down_revision = '9b95b190721e'
branch_labels = None
depends_on = None


def upgrade(engine_name):
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name):
    globals()["downgrade_%s" % engine_name]()


# ManageLocalTables._updateuser_byinterest() (loutilities/user/model.py) used to seed
# its "which rows already exist" lookup from active=True rows only. Once a localuser
# row's active flag went False, the next update_local_tables() call couldn't find it,
# so it inserted a duplicate row instead of updating the existing one -- one new
# duplicate per call, forever, for every inactive user. Fixed in loutilities#103
# (loutilities==3.13.0.dev2). This migration cleans up the rows that bug already
# created.
#
# Unlike members, no other table has a ForeignKey to contracts.localuser.id (confirmed
# via grep across dbmodel.py), so there's no FK-preference tier here -- just:
#   - prefer the active row
#   - else keep the lowest id (oldest row)
#
# A group is left untouched (no deletes at all) if more than one row in it is active --
# a genuine ambiguity this automated pass can't safely resolve; review those manually.
# Confirmed against a production-backup snapshot loaded into dev (2026-08-17): 14
# duplicate (user_id, interest_id) groups, 21,312 total rows. 10 groups fit the
# active-flag bug exactly (all rows inactive, cleaned automatically). The other 4
# groups (user_id 163 and 189, both interests) are a *different* bug: 4 exact-duplicate
# *active* rows each, all version_id=1 (never updated since insert) -- looks like a
# separate gunicorn-multi-worker race at boot (concurrent create_app() calls each
# independently inserting a new user's first row before any could see the others'
# insert), not the active-filter bug this migration targets. Left alone here
# deliberately; not yet resolved.
_DEDUP_LOCALUSER_SQL = """
WITH ranked AS (
    SELECT id,
           ROW_NUMBER() OVER (
               PARTITION BY user_id, interest_id
               ORDER BY active DESC, id ASC
           ) AS rn,
           COUNT(*) OVER (PARTITION BY user_id, interest_id) AS grp_count,
           SUM(active) OVER (PARTITION BY user_id, interest_id) AS grp_active_count
    FROM localuser
    WHERE user_id IS NOT NULL AND interest_id IS NOT NULL
)
DELETE FROM localuser WHERE id IN (
    SELECT id FROM (
        SELECT id FROM ranked
        WHERE grp_count > 1 AND rn > 1 AND grp_active_count <= 1
    ) AS to_delete
)
"""


def upgrade_():
    op.get_bind().execute(sa.text(_DEDUP_LOCALUSER_SQL))


def downgrade_():
    # data cleanup only -- deleted duplicate rows can't be reconstructed
    pass
