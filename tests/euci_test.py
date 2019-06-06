# Copyright 2020, CZ.NIC z.s.p.o. (http://www.nic.cz/)
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

from ipaddress import IPv4Address, IPv6Address
pytestmark = pytest.mark.uci_real  # TODO for now


def test_get_string(uci_setup):
    'Test get for no dtype (string in default)'
    uci_setup.set('test', (
        ("config", "str", "str"),
        ("option", "foo", "value"),
        ("list", "list", "value1"),
        ("list", "list", "value2"),
    ))
    u = euci.EUci(confdir=uci_setup.confdir())
    assert u.get('test', 'str', 'foo') == 'value'
    assert u.get('test', 'str', 'list') == ('value1', 'value2')


def test_set_string(uci_setup):
    'Test set for type string'
    uci_setup.set('test', (("config", "testing", "testing"),))
    u = euci.EUci(savedir=uci_setup.savedir(), confdir=uci_setup.confdir())
    u.set('test', 'testing', 'foo', 'value')
    u.set('test', 'testing', 'list', ('f', 'o', 'o'))
    assert u.get('test', 'testing', 'foo') == 'value'
    assert u.get('test', 'testing', 'list') == ('f', 'o', 'o')


def test_get_boolean(uci_setup):
    'Test get for dtype boolean'
    uci_setup.set('test', (
        ("config", "integer", "integer"),
        ("option", "false", "0"),
        ("option", "true", "1"),
        ("config", "word", "word"),
        ("option", "false", "no"),
        ("option", "true", "yes"),
        ("config", "state", "state"),
        ("option", "false", "off"),
        ("option", "true", "on"),
        ("config", "bool", "bool"),
        ("option", "false", "false"),
        ("option", "true", "true"),
        ("config", "bled", "bled"),
        ("option", "false", "disabled"),
        ("option", "true", "enabled"),
        ("config", "list", "list"),
        ("list", "true", "1"),
        ("list", "true", "yes"),
        ("list", "false", "0"),
        ("list", "false", "no"),
    ))
    u = euci.EUci(confdir=uci_setup.confdir())
    assert u.get('test', 'integer', 'true', dtype=bool)
    assert u.get('test', 'word', 'true', dtype=bool)
    assert u.get('test', 'state', 'true', dtype=bool)
    assert u.get('test', 'bool', 'true', dtype=bool)
    assert u.get('test', 'bled', 'true', dtype=bool)
    assert u.get('test', 'list', 'true', dtype=bool) == (True, True)
    assert not u.get('test', 'integer', 'false', dtype=bool)
    assert not u.get('test', 'word', 'false', dtype=bool)
    assert not u.get('test', 'state', 'false', dtype=bool)
    assert not u.get('test', 'bool', 'false', dtype=bool)
    assert not u.get('test', 'bled', 'false', dtype=bool)
    assert u.get('test', 'list', 'false', dtype=bool) == (False, False)


def test_set_boolean(uci_setup):
    'Test set for type boolean'
    uci_setup.set('test', (("config", "testing", "testing"),))
    u = euci.EUci(savedir=uci_setup.savedir(), confdir=uci_setup.confdir())
    u.set('test', 'testing', 'true', True)
    u.set('test', 'testing', 'false', False)
    u.set('test', 'testing', 'list', (True, False, True, False))
    assert u.get('test', 'testing', 'true') == '1'
    assert u.get('test', 'testing', 'false') == '0'
    assert u.get('test', 'testing', 'list') == ('1', '0', '1', '0')


def test_get_integer(uci_setup):
    'Test get for dtype int'
    uci_setup.set('test', (
        ("config", "integer", "integer"),
        ("option", "plus", "42"),
        ("option", "minus", "-42"),
        ("list", "primes", "2"),
        ("list", "primes", "3"),
        ("list", "primes", "5"),
        ("list", "primes", "7"),
    ))
    u = euci.EUci(confdir=uci_setup.confdir())
    assert u.get('test', 'integer', 'plus', dtype=int) == 42
    assert u.get('test', 'integer', 'minus', dtype=int) == -42
    assert u.get('test', 'integer', 'primes', dtype=int) == (2, 3, 5, 7)


def test_set_integer(uci_setup):
    'Test set for type int'
    uci_setup.set('test', (("config", "testing", "testing"),))
    u = euci.EUci(savedir=uci_setup.savedir(), confdir=uci_setup.confdir())
    u.set('test', 'testing', 'plus', 42)
    u.set('test', 'testing', 'minus', -42)
    u.set('test', 'testing', 'primes', (2, 3, 5, 7))
    assert u.get('test', 'testing', 'plus') == '42'
    assert u.get('test', 'testing', 'minus') == '-42'
    assert u.get('test', 'testing', 'primes') == ('2', '3', '5', '7')


def test_get_default(uci_setup):
    'Test get method with default value'
    uci_setup.set('test', (("config", "testing", "testing"),))
    u = euci.EUci(confdir=uci_setup.confdir())
    with pytest.raises(euci.UciExceptionNotFound):
        u.get('test', 'str', 'foo')
    assert u.get('test', 'str', 'foo', default='value') == 'value'
    assert u.get('test', 'str', 'foo', dtype=bool, default='true')
    assert u.get('test', 'str', 'foo', dtype=bool, default=True)
    assert u.get('test', 'str', 'foo', dtype=int, default=-42) == -42
    assert u.get('test', 'str', 'foo', dtype=int, default='-42') == -42


def test_context(uci_setup):
    'Test context with EUci'
    uci_setup.set('test', (
        ("config", "testing", "testing"),
        ("option", "one", "0"),
        ("option", "two", "1"),
    ))
    with euci.EUci(confdir=uci_setup.confdir()) as u:
        assert not u.get('test', 'testing', 'one', dtype=bool)
        assert u.get('test', 'testing', 'two', dtype=bool)


def test_get_list(uci_setup):
    'Test get with list'
    uci_setup.set('test', (
        ("config", "testing", "testing"),
        ("option", "option", "0"),
        ("list", "list", "0"),
        ("list", "list", "1"),
    ))
    u = euci.EUci(confdir=uci_setup.confdir())
    assert u.get('test', 'testing', 'option', dtype=bool, list=True) == (False,)
    assert not u.get('test', 'testing', 'option', dtype=bool, list=False)
    assert u.get('test', 'testing', 'list', dtype=bool, list=True) == (False, True)
    assert not u.get('test', 'testing', 'list', dtype=bool, list=False)


def test_ip_address_type(tmpdir):
    'Test ip address type'
    tmpdir.join('test').write(
        """
config testing 'testing'
    option option '0'
    option one '192.168.1.1'
    option two '::1'
    list three '::2'
    list three '10.0.0.1'
"""
    )
    with euci.EUci(confdir=tmpdir.strpath) as u:
        assert u.get('test', 'testing', 'one', dtype=IPv4Address) == IPv4Address('192.168.1.1')
        assert u.get('test', 'testing', 'one', dtype=IPv6Address) == IPv4Address('192.168.1.1')
        assert u.get('test', 'testing', 'two', dtype=IPv4Address) == IPv6Address('::1')
        assert u.get('test', 'testing', 'two', dtype=IPv6Address) == IPv6Address('::1')
        assert u.get('test', 'testing', 'three', dtype=IPv4Address, list=True) == (
            IPv6Address('::2'), IPv4Address('10.0.0.1')
        )
        assert u.get('test', 'testing', 'three', dtype=IPv6Address, list=True) == (
            IPv6Address('::2'), IPv4Address('10.0.0.1')
        )
