# Copyright 2019, CZ.NIC z.s.p.o. (http://www.nic.cz/)
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
import euci


def test_get_string(tmpdir):
    'Test get for no dtype (string in default)'
    tmpdir.join('test').write("""
config str 'str'
    option foo 'value'
""")
    u = euci.EUci(confdir=tmpdir.strpath)
    assert u.get('test', 'str', 'foo') == 'value'


def test_set_string(tmpdir):
    'Test set for type string'
    tmpdir.join('test').write("""
config testing 'testing'
""")
    u = euci.EUci(savedir=tmpdir.mkdir('save').strpath, confdir=tmpdir.strpath)
    u.set('test', 'testing', 'foo', 'value')
    assert u.get('test', 'testing', 'foo') == 'value'


def test_get_boolean(tmpdir):
    'Test get for dtype boolean'
    tmpdir.join('test').write("""
config integer 'integer'
    option true '1'
    option false '0'

config word 'word'
    option true 'yes'
    option false 'no'

config state 'state'
    option true 'on'
    option false 'off'

config bool 'bool'
    option true 'true'
    option false 'false'

config bled 'bled'
    option true 'enabled'
    option false 'disabled'
""")
    u = euci.EUci(confdir=tmpdir.strpath)
    assert u.get('test', 'integer', 'true', dtype=bool)
    assert u.get('test', 'word', 'true', dtype=bool)
    assert u.get('test', 'state', 'true', dtype=bool)
    assert u.get('test', 'bool', 'true', dtype=bool)
    assert u.get('test', 'bled', 'true', dtype=bool)
    assert not u.get('test', 'integer', 'false', dtype=bool)
    assert not u.get('test', 'word', 'false', dtype=bool)
    assert not u.get('test', 'state', 'false', dtype=bool)
    assert not u.get('test', 'bool', 'false', dtype=bool)
    assert not u.get('test', 'bled', 'false', dtype=bool)


def test_set_boolean(tmpdir):
    'Test set for type boolean'
    tmpdir.join('test').write("""
config testing 'testing'
""")
    u = euci.EUci(savedir=tmpdir.mkdir('save').strpath, confdir=tmpdir.strpath)
    u.set('test', 'testing', 'true', True)
    u.set('test', 'testing', 'false', False)
    assert u.get('test', 'testing', 'true') == '1'
    assert u.get('test', 'testing', 'false') == '0'


def test_get_integer(tmpdir):
    'Test get for dtype int'
    tmpdir.join('test').write("""
config integer 'integer'
    option plus '42'
    option minus '-42'
""")
    u = euci.EUci(confdir=tmpdir.strpath)
    assert u.get('test', 'integer', 'plus', dtype=int) == 42
    assert u.get('test', 'integer', 'minus', dtype=int) == -42


def test_set_integer(tmpdir):
    'Test set for type int'
    tmpdir.join('test').write("""
config testing 'testing'
""")
    u = euci.EUci(savedir=tmpdir.mkdir('save').strpath, confdir=tmpdir.strpath)
    u.set('test', 'testing', 'plus', 42)
    u.set('test', 'testing', 'minus', -42)
    assert u.get('test', 'testing', 'plus') == '42'
    assert u.get('test', 'testing', 'minus') == '-42'


def test_get_default(tmpdir):
    'Test get method with default value'
    tmpdir.join('test').write("""
config testing 'testing'
""")
    u = euci.EUci(confdir=tmpdir.strpath)
    with pytest.raises(euci.UciExceptionNotFound):
        u.get('test', 'str', 'foo')
    assert u.get('test', 'str', 'foo', default='value') == 'value'
    assert u.get('test', 'str', 'foo', dtype=bool, default='true')
    assert u.get('test', 'str', 'foo', dtype=bool, default=True)
    assert u.get('test', 'str', 'foo', dtype=int, default=-42) == -42
    assert u.get('test', 'str', 'foo', dtype=int, default='-42') == -42


def test_context(tmpdir):
    'Test context with EUci'
    tmpdir.join('test').write("""
config testing 'testing'
    option one '0'
    option two '1'
""")
    with euci.EUci(confdir=tmpdir.strpath) as u:
        assert not u.get('test', 'testing', 'one', dtype=bool)
        assert u.get('test', 'testing', 'two', dtype=bool)
