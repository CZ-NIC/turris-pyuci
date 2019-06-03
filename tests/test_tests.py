"""These tests are intended to tests that helper functions implemented in this
test framework are working correctly.
"""
import pytest

CONTENT_PARSED = (
    ("config", "testing", "testing"),
    ("option", "zero", '0'),
    ("option", "one", '1'),
    ("config", "anonymous"),
    ("option", "password", "12345"),
    ("config", "testlist", "testlist"),
    ("list", "list1", "once"),
    ("list", "list1", "twice"),
    ("list", "list2", "42"),
)
CONTENT_PLAIN = """
config testing 'testing'
\toption zero '0'
\toption one '1'

config anonymous
\toption password '12345'

config testlist 'testlist'
\tlist list1 'once'
\tlist list1 'twice'
\tlist list2 '42'

"""


@pytest.mark.uci_real
def test_setup_set(uci_setup):
    """Test that uci setup is generating files in correct format.
    """
    uci_setup.set('test', CONTENT_PARSED)
    assert uci_setup.tmpdir.join('conf', 'test').read() == CONTENT_PLAIN


@pytest.mark.uci_real
def test_setup_get(uci_setup):
    """Test that uci setup can parse correctly files.
    """
    uci_setup.tmpdir.mkdir('conf')
    uci_setup.tmpdir.join('conf', 'test').write(CONTENT_PLAIN)
    assert uci_setup.get('test') == CONTENT_PARSED


@pytest.mark.uci_real
def test_setup_get_saved(uci_setup):
    """Test that uci setup can parse correctly saved files.
    """
    uci_setup.tmpdir.mkdir('save')
    uci_setup.tmpdir.join('save', 'test').write('''test.testing="testing"
test.testing.optimal="value"
''')
    assert uci_setup.get_save('test') == (
        ('test.testing', 'testing'),
        ('test.testing.optimal', 'value'),
    )
