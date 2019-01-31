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


def test_boolean_get(tmpdir):
    'Test get_boolean'
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
    assert u.get_boolean('test', 'integer', 'true')
    assert u.get_boolean('test', 'word', 'true')
    assert u.get_boolean('test', 'state', 'true')
    assert u.get_boolean('test', 'bool', 'true')
    assert u.get_boolean('test', 'bled', 'true')
    assert not u.get_boolean('test', 'integer', 'false')
    assert not u.get_boolean('test', 'word', 'false')
    assert not u.get_boolean('test', 'state', 'false')
    assert not u.get_boolean('test', 'bool', 'false')
    assert not u.get_boolean('test', 'bled', 'false')


def test_boolean_set(tmpdir):
    'Test set_boolean'
    tmpdir.join('test').write("""
config testing 'testing'
""")
    u = euci.EUci(savedir=tmpdir.mkdir('save').strpath, confdir=tmpdir.strpath)
    u.set_boolean('test', 'testing', 'true', True)
    u.set_boolean('test', 'testing', 'false', False)
    assert u.get('test', 'testing', 'true') == '1'
    assert u.get('test', 'testing', 'false') == '0'


def test_integer_get(tmpdir):
    'Test get_integer'
    tmpdir.join('test').write("""
config integer 'integer'
    option plus '42'
    option minus '-42'
""")
    u = euci.EUci(confdir=tmpdir.strpath)
    assert u.get_integer('test', 'integer', 'plus') == 42
    assert u.get_integer('test', 'integer', 'minus') == -42


def test_integer_set(tmpdir):
    'Test set_integer'
    tmpdir.join('test').write("""
config testing 'testing'
""")
    u = euci.EUci(savedir=tmpdir.mkdir('save').strpath, confdir=tmpdir.strpath)
    u.set_integer('test', 'testing', 'plus', 42)
    u.set_integer('test', 'testing', 'minus', -42)
    assert u.get('test', 'testing', 'plus') == '42'
    assert u.get('test', 'testing', 'minus') == '-42'
