"""Mockup of Unified configuration interface bindings
"""
import os
import sys
import pytest
from . import uci


def uci_monkeypatch():
    """Set uci from uci_monkey as prefered one.
    """
    _sysdir_uci = os.path.dirname(__file__)
    if _sysdir_uci not in sys.path:
        sys.path.insert(0, _sysdir_uci)


@pytest.fixture
def fake_uci():
    """Fixture to provide you with faked uci state. You can use it to set and
    verify UCI state.
    """
    from . import guts
    state = guts.UciState()
    yield state
    state.wipe()
