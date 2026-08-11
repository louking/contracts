'''
test_contractmanager - test contracts.contractmanager
=========================================================
'''

# pypi
import pytest
from flask import Flask

# homegrown
from contracts.contractmanager import (
    _evaluate, recursive_render, ContractManagerTemplate, ContractManager, parameterError,
)


class Obj:
    '''plain object with an instance __dict__, standing in for mergefields'''
    pass


class Callable:
    '''_evaluate() only invokes callables lacking a __dict__ (it treats anything with
    a __dict__, including ordinary functions/lambdas/bound methods, as a nested object
    to recurse into rather than as a leaf to call) -- __slots__ is what makes this a
    genuine "no __dict__" callable leaf, matching what _evaluate()'s docstring describes.
    '''
    __slots__ = ('fn',)

    def __init__(self, fn):
        self.fn = fn

    def __call__(self, tree):
        return self.fn(tree)


@pytest.fixture
def app():
    return Flask(__name__)


# ----------------------------------------------------------------------
# _evaluate
# ----------------------------------------------------------------------

def test_evaluate_leaves_plain_attrs_alone():
    tree = Obj()
    tree.a = 'hello'

    result = _evaluate(tree, tree)

    assert result.a == 'hello'


def test_evaluate_calls_callable_attrs_with_tree():
    tree = Obj()
    tree.a = 'hello'
    tree.b = Callable(lambda t: 'computed-{}'.format(t.a))

    result = _evaluate(tree, tree)

    assert result.b == 'computed-hello'


def test_evaluate_does_not_call_ordinary_functions_or_lambdas():
    # gotcha: a plain function/lambda has its own __dict__ (even if empty), so
    # _evaluate() treats it as a nested object to recurse into (a no-op, since it has
    # no attributes) rather than as a callable leaf to invoke -- it comes back unchanged
    tree = Obj()
    tree.a = 'hello'
    marker = lambda t: 'computed-{}'.format(t.a)
    tree.b = marker

    result = _evaluate(tree, tree)

    assert result.b is marker


def test_evaluate_recurses_into_list_items():
    tree = Obj()
    item1 = Obj()
    item1.x = Callable(lambda t: 'x-value')
    item2 = Obj()
    item2.x = 'plain'
    tree.items = [item1, item2]

    result = _evaluate(tree, tree)

    assert result.items[0].x == 'x-value'
    assert result.items[1].x == 'plain'

def test_evaluate_recurses_into_nested_objects():
    tree = Obj()
    child = Obj()
    child.a = Callable(lambda t: 'nested-{}'.format(t.top))
    tree.top = 'level'
    tree.child = child

    result = _evaluate(tree, tree)

    assert result.child.a == 'nested-level'


def test_evaluate_skips_private_attrs():
    tree = Obj()
    marker = lambda t: 'should not be called'
    tree._private = marker

    result = _evaluate(tree, tree)

    assert result._private is marker


# ----------------------------------------------------------------------
# recursive_render
# ----------------------------------------------------------------------

def test_recursive_render_simple_substitution(app):
    with app.app_context():
        result = recursive_render('Hello {{ name }}', {'name': 'World'})

    assert result == 'Hello World'


def test_recursive_render_expands_until_stable(app):
    # 'outer' itself renders to template text referencing 'inner'; recursive_render
    # keeps re-rendering the *result* against the same values until it stops changing
    with app.app_context():
        result = recursive_render('{{ outer }}', {'outer': '{{ inner }}', 'inner': 'done'})

    assert result == 'done'


def test_recursive_render_no_template_syntax_returns_as_is(app):
    with app.app_context():
        result = recursive_render('plain text', {})

    assert result == 'plain text'


# ----------------------------------------------------------------------
# ContractManagerTemplate
# ----------------------------------------------------------------------

def test_contractmanagertemplate_render(app):
    merge = Obj()
    merge.name = 'World'

    with app.app_context():
        tpl = ContractManagerTemplate('Hello {{ name }}')
        result = tpl.render(merge)

    assert result == 'Hello World'


def test_contractmanagertemplate_render_evaluates_callables(app):
    merge = Obj()
    merge.first = 'Jo'
    merge.full = Callable(lambda t: '{} Smith'.format(t.first))

    with app.app_context():
        tpl = ContractManagerTemplate('{{ full }}')
        result = tpl.render(merge)

    assert result == 'Jo Smith'


def test_contractmanagertemplate_generate_yields_loop_output(app):
    merge = Obj()
    merge.items = ['a', 'b', 'c']

    with app.app_context():
        tpl = ContractManagerTemplate('{% for i in items %}{{ i }}\n{% endfor %}')
        result = ''.join(tpl.generate(merge))

    assert result == 'a\nb\nc\n'


# ----------------------------------------------------------------------
# ContractManager.__init__
# ----------------------------------------------------------------------

def test_contractmanager_defaults():
    cm = ContractManager()

    assert cm.contractType is None
    assert cm.templateType is None
    assert cm.driveFolderId is None
    assert cm.doctype == 'docx'


def test_contractmanager_kwargs_override_defaults():
    cm = ContractManager(contractType='Quote', templateType='Standard', doctype='html')

    assert cm.contractType == 'Quote'
    assert cm.templateType == 'Standard'
    assert cm.doctype == 'html'


def test_contractmanager_invalid_doctype_raises():
    with pytest.raises(parameterError):
        ContractManager(doctype='pdf')
