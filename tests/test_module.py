# Copyright 2018, CZ.NIC z.s.p.o. (http://www.nic.cz/)
#
# This file is part of the PyUCI.
#
# PyUCI is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
# PyUCI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyUCI.  If not, see <http://www.gnu.org/licenses/>.
import pytest
import uci


def test_init():
    'Test class __init__ and __del__'
    assert uci.Uci() is not None


def test_get(tmpdir):
    'Test get method. This depends on working test_init.'
    tmpdir.join('test').write("""
config testing 'testing'
    option one '0'
    option two '1'

config testlist 'testlist'
    list list1 '42'
    list list2 'once'
    list list2 'twice'
    list list2 'thrice'
""")
    u = uci.Uci(confdir=tmpdir.strpath)
    assert u.get('test', 'testing') == 'testing'
    assert u.get('test', 'testing', 'one') == '0'
    assert u.get('test', 'testing', 'two') == '1'
    assert u.get('test', 'testlist', 'list1') == ('42',)
    assert u.get('test', 'testlist', 'list2') == ('once', 'twice', 'thrice')


def test_set(tmpdir):
    'Test set method. This depends on working test_get.'
    tmpdir.join('test').write("")
    u = uci.Uci(savedir=tmpdir.mkdir('save').strpath, confdir=tmpdir.strpath)
    u.set('test', 'testing', 'testing')
    u.set('test', 'testing', 'variable', 'value')
    assert u.get('test', 'testing') == 'testing'
    assert u.get('test', 'testing', 'variable') == 'value'


def test_commit(tmpdir):
    'Test commit method. This depends on working test_set.'
    cnf = tmpdir.join('test')
    cnf.write("")
    u = uci.Uci(savedir=tmpdir.mkdir('save').strpath, confdir=tmpdir.strpath)
    u.set('test', 'testing', 'testing')
    u.set('test', 'testing', 'variable', 'value')
    u.commit('test')
    assert cnf.read() == """
config testing 'testing'
\toption variable 'value'

"""


def test_delete(tmpdir):
    'Test delete method. This depends on working test_get.'
    tmpdir.join('test').write("""
config testing 'testing'
    option one '0'
    option two '1'
""")
    u = uci.Uci(confdir=tmpdir.strpath)
    u.delete('test', 'testing', 'one')
    assert u.get('test', 'testing', 'two') == '1'
    with pytest.raises(uci.UciExceptionNotFound):
        u.get('test', 'testing', 'one')
    u.delete('test', 'testing')
    with pytest.raises(uci.UciExceptionNotFound):
        u.get('test', 'testing', 'two')
    with pytest.raises(uci.UciExceptionNotFound):
        u.get('test', 'testing')


def test_rename(tmpdir):
    'Test delete method. This depends on working test_get.'
    tmpdir.join('test').write("""
config testing 'testing'
    option one '0'
    option two '1'
""")
    u = uci.Uci(confdir=tmpdir.strpath)
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


def no_test_reorder(tmpdir):
    'Test delete method. This depends on working test_commit.'
    cnf = tmpdir.join('test')
    cnf.write("""
config testing 'testing'
    option one '0'

config deploy 'deploy'
    option two '1'

""")
    u = uci.Uci(confdir=tmpdir.strpath)
    u.reorder('test', 'testing', 1)
    u.commit('test')
    assert cnf.read() == """
config deploy 'deploy'
\toption two '1'

config testing 'testing'
\toption one '0'

"""


def test_save(tmpdir):
    'Test save method. This depends on working test_set.'
    sf = tmpdir.mkdir('save')
    cnf = tmpdir.mkdir('conf')
    cnf.join('test').write("")
    u = uci.Uci(savedir=sf.strpath, confdir=cnf.strpath)
    u.set('test', 'testing', 'testing')
    u.set('test', 'testing', 'variable', 'value')
    u.save('test')
    assert sf.join('test').read() == """test.testing='testing'
test.testing.variable='value'
"""


def test_revert(tmpdir):
    'Test revert method. This depends on working test_set.'
    tmpdir.join('test').write("")
    u = uci.Uci(confdir=tmpdir.strpath)
    u.set('test', 'testing', 'testing')
    u.set('test', 'testing', 'variable', 'value')
    assert u.get('test', 'testing', 'variable') == 'value'
    u.revert('test')
    with pytest.raises(uci.UciExceptionNotFound):
        u.get('test', 'testing', 'variable')


def test_list_configs(tmpdir):
    'Test list_configs method.'
    tmpdir.join('test').write("")
    tmpdir.join('deploy').write("")
    u = uci.Uci(confdir=tmpdir.strpath)
    assert u.list_configs() == ['deploy', 'test']


def test_context(tmpdir):
    'Test context with Uci. This depends on working test_get.'
    tmpdir.join('test').write("""
config testing 'testing'
    option one '0'
    option two '1'
""")
    with uci.Uci(confdir=tmpdir.strpath) as u:
        assert u.get('test', 'testing', 'one') == '0'
        assert u.get('test', 'testing', 'two') == '1'


def test_context_commit(tmpdir):
    """Test that when we leave context that we commit. This depends on working
    test_set.
    """
    tmpdir.join('test').write("")
    with uci.Uci(confdir=tmpdir.strpath) as u:
        u.set('test', 'testing', 'testing')
        u.set('test', 'testing', 'one', '0')
        u.set('test', 'testing', 'two', '1')
    with uci.Uci(confdir=tmpdir.strpath) as u:
        assert u.get('test', 'testing', 'one') == '0'
        assert u.get('test', 'testing', 'two') == '1'
