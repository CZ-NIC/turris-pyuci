"""These are tests for uci package.
"""
import pytest
import uci

pytestmark = pytest.mark.uci_real  # TODO for now


def test_init():
    'Test class __init__ and __del__'
    assert uci.Uci() is not None


def test_get(uci_setup):
    'Test get method. This depends on working test_init.'
    uci_setup.set('test', (
        ("config", "testing", "testing"),
        ("option", "one", "0"),
        ("option", "two", "1"),
        ("config", "testlist", "testlist"),
        ("list", "list1", "42"),
        ("list", "list2", "once"),
        ("list", "list2", "twice"),
        ("list", "list2", "thrice"),
    ))
    u = uci.Uci(confdir=uci_setup.confdir())
    assert u.get('test', 'testing') == 'testing'
    assert u.get('test', 'testing', 'one') == '0'
    assert u.get('test', 'testing', 'two') == '1'
    assert u.get('test', 'testlist', 'list1') == ('42',)
    assert u.get('test', 'testlist', 'list2') == ('once', 'twice', 'thrice')


def test_set(uci_setup):
    'Test set method. This depends on working test_get.'
    uci_setup.set('test', ())
    u = uci.Uci(savedir=uci_setup.savedir(), confdir=uci_setup.confdir())
    u.set('test', 'testing', 'testing')
    u.set('test', 'testing', 'variable', 'value')
    assert u.get('test', 'testing') == 'testing'
    assert u.get('test', 'testing', 'variable') == 'value'


def test_commit(uci_setup):
    'Test commit method. This depends on working test_set.'
    uci_setup.set('test', ())
    u = uci.Uci(savedir=uci_setup.savedir(), confdir=uci_setup.confdir())
    u.set('test', 'testing', 'testing')
    u.set('test', 'testing', 'variable', 'value')
    assert uci_setup.get('test') == ()
    u.commit('test')
    assert uci_setup.get('test') == (
        ("config", "testing", "testing"),
        ("option", "variable", "value"),
    )


def test_delete(uci_setup):
    'Test delete method. This depends on working test_get.'
    uci_setup.set('test', (
        ("config", "testing", "testing"),
        ("option", "one", "0"),
        ("option", "two", "1"),
    ))
    u = uci.Uci(confdir=uci_setup.confdir())
    u.delete('test', 'testing', 'one')
    assert u.get('test', 'testing', 'two') == '1'
    with pytest.raises(uci.UciExceptionNotFound):
        u.get('test', 'testing', 'one')
    u.delete('test', 'testing')
    with pytest.raises(uci.UciExceptionNotFound):
        u.get('test', 'testing', 'two')
    with pytest.raises(uci.UciExceptionNotFound):
        u.get('test', 'testing')


def test_rename(uci_setup):
    'Test rename method. This depends on working test_get.'
    uci_setup.set('test', (
        ("config", "testing", "testing"),
        ("option", "one", "0"),
        ("option", "two", "1"),
    ))
    u = uci.Uci(confdir=uci_setup.confdir())
    u.rename('test', 'testing', 'one', 'three')
    with pytest.raises(uci.UciExceptionNotFound):
        u.get('test', 'testing', 'one')
    assert u.get('test', 'testing', 'three') == '0'
    u.rename('test', 'testing', 'deploy')
    with pytest.raises(uci.UciExceptionNotFound):
        u.get('test', 'testing', 'three')
    with pytest.raises(uci.UciExceptionNotFound):
        u.get('test', 'testing', 'two')
    assert u.get('test', 'deploy', 'three') == '0'
    assert u.get('test', 'deploy', 'two') == '1'


def no_test_reorder(uci_setup):
    'Test reorder method. This depends on working test_commit.'
    uci_setup.set('test', (
        ("config", "testing", "testing"),
        ("option", "two", "1"),
        ("config", "deploy", "deploy"),
        ("option", "one", "0"),
    ))
    u = uci.Uci(confdir=uci_setup.confdir())
    u.reorder('test', 'testing', 1)
    u.commit('test')
    assert uci_setup.get('test') == (
        ("config", "deploy", "deploy"),
        ("option", "one", "0"),
        ("config", "testing", "testing"),
        ("option", "two", "1"),
    )


def test_save(uci_setup):
    'Test save method. This depends on working test_set.'
    uci_setup.set('test', ())
    u = uci.Uci(savedir=uci_setup.savedir(), confdir=uci_setup.confdir())
    u.set('test', 'testing', 'testing')
    u.set('test', 'testing', 'variable', 'value')
    u.save('test')
    assert uci_setup.get_save('test') == (
        ("test.testing", "testing"),
        ("test.testing.variable", "value"),
    )


def test_revert(uci_setup):
    'Test revert method. This depends on working test_set.'
    uci_setup.set('test', ())
    u = uci.Uci(confdir=uci_setup.confdir())
    u.set('test', 'testing', 'testing')
    u.set('test', 'testing', 'variable', 'value')
    assert u.get('test', 'testing', 'variable') == 'value'
    u.revert('test')
    with pytest.raises(uci.UciExceptionNotFound):
        u.get('test', 'testing', 'variable')


def test_list_configs(uci_setup):
    'Test list_configs method.'
    uci_setup.set('test', ())
    uci_setup.set('deploy', ())
    u = uci.Uci(confdir=uci_setup.confdir())
    assert u.list_configs() == ['deploy', 'test']


def test_context(uci_setup):
    'Test context with Uci. This depends on working test_get.'
    uci_setup.set('test', (
        ("config", "testing", "testing"),
        ("option", "one", "0"),
        ("option", "two", "1"),
    ))
    with uci.Uci(confdir=uci_setup.confdir()) as u:
        assert u.get('test', 'testing', 'one') == '0'
        assert u.get('test', 'testing', 'two') == '1'


def test_context_commit(uci_setup):
    """Test that when we leave context that we commit. This depends on working
    test_set.
    """
    uci_setup.set('test', ())
    with uci.Uci(confdir=uci_setup.confdir()) as u:
        u.set('test', 'testing', 'testing')
        u.set('test', 'testing', 'one', '0')
        u.set('test', 'testing', 'two', '1')
    with uci.Uci(confdir=uci_setup.confdir()) as u:
        assert u.get('test', 'testing', 'one') == '0'
        assert u.get('test', 'testing', 'two') == '1'
