import pytest
import uci
from uci_monkey import guts

pytestmark = pytest.mark.uci_monkey


def test_uci_fake_fixture(uci_fake):
    assert uci.current_state == uci_fake


def test_invalid_set(uci_fake):
    with pytest.raises(guts.InvalidUciSpecException):
        uci_fake["test"] = "value"
    with pytest.raises(guts.InvalidUciSpecException):
        uci_fake["test.this.four.sections"] = "value"
    with pytest.raises(guts.InvalidUciSpecException):
        uci_fake["test.this[]"] = "value"
    with pytest.raises(guts.InvalidUciSpecException):
        uci_fake["test.@this[]"] = "value"
    with pytest.raises(guts.InvalidUciSpecException):
        uci_fake["test.@this[]"] = "value"


def test_value(uci_fake):
    uci_fake["test.testing"] = "testing"
    assert uci_fake["test.testing"] == "testing"


def test_list(uci_fake):
    uci_fake["test.testing.list"] = ("once", "twice")
    assert uci_fake["test.testing.list"] == ["once", "twice"]
    uci_fake["test.testing.list"].append("thrice")
    assert uci_fake["test.testing.list"] == ["once", "twice", "thrice"]


def test_section_list(uci_fake):
    uci_fake["test.list"] = ("once", "twice")
    assert isinstance(uci_fake["test.list"], str)


def test_missing(uci_fake):
    with pytest.raises(KeyError):
        uci_fake["test"]
    with pytest.raises(KeyError):
        uci_fake["test.list"]
