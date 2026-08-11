'''
test_dbmodel - test contracts.dbmodel
=========================================================
'''

# homegrown
from contracts.dbmodel import db, DateRule, Tag, ModelItem, getmodelitems, initdbmodels


# ----------------------------------------------------------------------
# DateRule.__init__ rulename generation
# ----------------------------------------------------------------------

def test_rulename_nth_weekday():
    rule = DateRule(rule='Second', day='Tue', month='Mar')
    assert rule.rulename == 'Second Tue Mar'


def test_rulename_nth_weekday_with_year():
    rule = DateRule(rule='Second', day='Tue', month='Mar', year=2026)
    assert rule.rulename == 'Second Tue Mar, 2026'


def test_rulename_nth_weekday_with_deltaday():
    rule = DateRule(rule='Second', day='Tue', month='Mar', deltaday=-2)
    assert rule.rulename == 'Second Tue Mar, -2 days from'


def test_rulename_nth_weekday_with_addldays():
    rule = DateRule(rule='Second', day='Tue', month='Mar', addldays=3)
    assert rule.rulename == "Second Tue Mar, 3 add'l days"


def test_rulename_easter():
    rule = DateRule(rule='Easter')
    assert rule.rulename == 'Easter'


def test_rulename_date_without_year():
    rule = DateRule(rule='Date', month='Jul', date=4)
    assert rule.rulename == 'Jul 4'


def test_rulename_date_with_year():
    rule = DateRule(rule='Date', month='Jul', date=4, year=2020)
    assert rule.rulename == 'Jul 4, 2020'


# ----------------------------------------------------------------------
# getmodelitems
# ----------------------------------------------------------------------

def test_getmodelitems_scalar_query_returns_single_item(bare_dbapp):
    tag = Tag(tag='foo', description='foo tag', isBuiltIn=True)
    db.session.add(tag)
    db.session.commit()

    getter = getmodelitems(Tag, {'tag': 'foo'})
    result = getter()
    assert result.id == tag.id


def test_getmodelitems_list_query_returns_list(bare_dbapp):
    tag1 = Tag(tag='foo', description='foo tag', isBuiltIn=True)
    tag2 = Tag(tag='bar', description='bar tag', isBuiltIn=True)
    db.session.add_all([tag1, tag2])
    db.session.commit()

    getter = getmodelitems(Tag, [{'tag': 'foo'}, {'tag': 'bar'}])
    result = getter()
    assert [r.id for r in result] == [tag1.id, tag2.id]


def test_getmodelitems_resolves_callable_query_values(bare_dbapp):
    tag = Tag(tag='foo', description='foo tag', isBuiltIn=True)
    db.session.add(tag)
    db.session.commit()

    getter = getmodelitems(Tag, {'tag': lambda: 'foo'})
    result = getter()
    assert result.id == tag.id


# ----------------------------------------------------------------------
# initdbmodels
# ----------------------------------------------------------------------

def test_initdbmodels_cleartable_adds_items(bare_dbapp):
    items = [
        {'tag': 'foo', 'description': 'foo tag', 'isBuiltIn': True},
        {'tag': 'bar', 'description': 'bar tag', 'isBuiltIn': True},
    ]
    initdbmodels([ModelItem(Tag, items, cleartable=True)])

    tags = {t.tag: t.description for t in Tag.query.all()}
    assert tags == {'foo': 'foo tag', 'bar': 'bar tag'}


def test_initdbmodels_cleartable_removes_preexisting_rows(bare_dbapp):
    db.session.add(Tag(tag='stale', description='old', isBuiltIn=True))
    db.session.commit()

    initdbmodels([ModelItem(Tag, [{'tag': 'fresh', 'description': 'new', 'isBuiltIn': True}], cleartable=True)])

    tags = [t.tag for t in Tag.query.all()]
    assert tags == ['fresh']


def test_initdbmodels_merge_updates_existing_matching_checkkey(bare_dbapp):
    db.session.add(Tag(tag='foo', description='old description', isBuiltIn=True))
    db.session.commit()

    items = [{'tag': 'foo', 'description': 'new description', 'isBuiltIn': True}]
    initdbmodels([ModelItem(Tag, items, cleartable=False, checkkeys=['tag'])])

    tag = Tag.query.filter_by(tag='foo').one()
    assert tag.description == 'new description'
    assert Tag.query.count() == 1


def test_initdbmodels_merge_adds_new_row_when_no_match(bare_dbapp):
    db.session.add(Tag(tag='foo', description='existing', isBuiltIn=True))
    db.session.commit()

    items = [{'tag': 'bar', 'description': 'new tag', 'isBuiltIn': True}]
    initdbmodels([ModelItem(Tag, items, cleartable=False, checkkeys=['tag'])])

    tags = {t.tag for t in Tag.query.all()}
    assert tags == {'foo', 'bar'}


def test_initdbmodels_merge_uses_callable_checkkeys(bare_dbapp):
    existing = Tag(tag='foo', description='existing', isBuiltIn=True)
    db.session.add(existing)
    db.session.commit()

    def itemexists(item):
        return Tag.query.filter_by(tag=item['tag']).one_or_none()

    items = [{'tag': 'foo', 'description': 'updated via callable', 'isBuiltIn': True}]
    initdbmodels([ModelItem(Tag, items, cleartable=False, checkkeys=itemexists)])

    tag = Tag.query.filter_by(tag='foo').one()
    assert tag.description == 'updated via callable'
