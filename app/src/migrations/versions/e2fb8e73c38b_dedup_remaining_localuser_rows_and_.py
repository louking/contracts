"""dedup remaining exact-duplicate localuser rows and enforce uniqueness (louking/contracts#578)

Revision ID: e2fb8e73c38b
Revises: 1665dbdd59c5
Create Date: 2026-08-17 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e2fb8e73c38b'
down_revision = '1665dbdd59c5'
branch_labels = None
depends_on = None


def upgrade(engine_name):
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name):
    globals()["downgrade_%s" % engine_name]()


# 1665dbdd59c5 left any (user_id, interest_id) group alone if more than one row in it was
# active, since it couldn't tell which active row was "correct". louking/contracts#578 root-
# caused those leftover groups: contracts runs multiple gunicorn workers, and each one
# independently calls update_local_tables() at boot. ManageLocalTables.update()
# (loutilities/user/model.py) had no locking, so concurrently booting workers could each find
# no existing localuser row for a newly-synced (user_id, interest_id) and insert their own --
# one duplicate row per worker, racing before any could see the others' insert. update() now
# takes a lockfile (see contracts/dbmodel.py:update_local_tables(), loutilities>=3.13.1) that
# serializes those workers, so this specific race can't recur -- but the rows it already
# created are still sitting in the table.
#
# Confirmed by inspection (production, and a production-backup snapshot loaded into dev,
# 2026-08-17): every row in every leftover group is byte-identical to its groupmates in every
# copied field (email, name, given_name, active) -- only `id` differs. That's expected: all
# copied fields trace back to the same, unchanged master User row, and update_local_tables()'s
# per-boot sync only ever tracks one row per (user_id, interest_id) key (a plain dict keyed on
# that pair silently drops earlier duplicates as it builds its working set), so the orphaned
# duplicates were never touched again after their original insert -- nothing left to diverge.
#
# This migration re-runs the same dedup shape as 1665dbdd59c5 (rank by active DESC, id ASC;
# keep rn=1) but replaces the "leave it alone if more than one active" guard with an explicit
# content-equality check: a group is only collapsed if every row in it has identical (email,
# name, given_name, active). Any group that doesn't -- a real ambiguity, not a duplicate -- is
# still left alone for manual review, same as before.
#
# Then adds a UNIQUE constraint on (user_id, interest_id) so this class of duplicate can't be
# created again by any future bug -- defense in depth alongside the update() locking fix. MySQL
# does not enforce uniqueness among NULLs, so rows with NULL user_id or interest_id (e.g. the
# orphaned-interest corner case from louking/webmodules#44) are unaffected. If this constraint
# fails to apply, some environment still has a leftover ambiguous (non-identical) group that
# needs manual review before this migration can proceed.
_DEDUP_LOCALUSER_SQL = """
WITH content AS (
    SELECT id, user_id, interest_id, active,
           CONCAT_WS(CHAR(1), email, name, given_name, CAST(active AS CHAR)) AS content
    FROM localuser
    WHERE user_id IS NOT NULL AND interest_id IS NOT NULL
),
ranked AS (
    SELECT id,
           ROW_NUMBER() OVER (
               PARTITION BY user_id, interest_id
               ORDER BY active DESC, id ASC
           ) AS rn,
           COUNT(*) OVER (PARTITION BY user_id, interest_id) AS grp_count,
           MIN(content) OVER (PARTITION BY user_id, interest_id) AS min_content,
           MAX(content) OVER (PARTITION BY user_id, interest_id) AS max_content
    FROM content
)
DELETE FROM localuser WHERE id IN (
    SELECT id FROM (
        SELECT id FROM ranked
        WHERE grp_count > 1 AND rn > 1 AND min_content = max_content
    ) AS to_delete
)
"""


def upgrade_():
    op.get_bind().execute(sa.text(_DEDUP_LOCALUSER_SQL))
    op.create_unique_constraint('uq_localuser_user_interest', 'localuser', ['user_id', 'interest_id'])


def downgrade_():
    op.drop_constraint('uq_localuser_user_interest', 'localuser', type_='unique')
    # data cleanup only -- deleted duplicate rows can't be reconstructed
