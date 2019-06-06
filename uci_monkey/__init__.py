"""Mockup of Unified configuration interface bindings
"""
import sys
import pytest
from . import uci


def uci_monkeypatch():
    """Set uci from uci_monkey as uci module
    """
    sys.modules["uci"] = uci


@pytest.fixture
def uci_fake():
    """Fixture to provide you with faked uci state. You can use it to set and
    verify UCI state.
    """
    from . import guts
    uci.current_state = guts.UciState()
    yield uci.current_state
    uci.current_state = None
