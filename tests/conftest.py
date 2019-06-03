import os
import pytest
from uci_monkey import *


def pytest_addoption(parser):
    parser.addoption(
        "-M", "--monkey",
        action="store_true",
        help="Run tests with fake uci."
    )


def pytest_configure(config):
    # Add dynamic markers
    config.addinivalue_line("markers", "uci_monkey: mark test to be run only with fake uci")
    config.addinivalue_line("markers", "uci_real: mark test to be run only with real uci")
    # Force to use fake uci
    if config.getoption("-M"):
        uci_monkeypatch()


def pytest_runtest_setup(item):
    monkey = item.config.getoption("-M")
    if monkey and item.get_closest_marker(name="uci_real", default=False):
        pytest.skip("test is not intended for fake uci")
    elif not monkey and item.get_closest_marker(name="uci_monkey", default=False):
        pytest.skip("test is not intended for real uci")


###############################################################################


class UciSetup:
    """Generic class providing backend access to UCI.
    """

    def set(self, config, content):
        """Sets given content of for given config.
        Content has to be tuple of tuple lines. Every tuple for line can be at
        most three fields but at minimum two. Case where only two fields are
        provided is for anonymous config sections.
        """
        raise NotImplementedError

    def get(self, config):
        """Verifies content of saved configuration.
        Returns content of config in same form as in case of set.
        """
        raise NotImplementedError

    def get_save(self, config):
        """Returns tuple of tuple pairs of config and value.
        Following line:
            config.section=value
        is parsed to:
            ("config.section", "value")
        """
        raise NotImplementedError

    def confdir(self):
        """Returns configuration directory path. Please use it only for Uci or
        Euci object configuration. It might have bogus value if monkey uci is
        used.
        """
        raise NotImplementedError

    def savedir(self):
        """Returns save directory path. Please use it only for Uci or Euci
        object configuration. It might have bogus value if monkey uci is used.
        """
        raise NotImplementedError


class RealUciSetup(UciSetup):
    """Class implementing backend access for tests ucing real UCI.
    """

    def __init__(self, tmpdir):
        self.tmpdir = tmpdir

    def set(self, config, content):
        self._safemkdir('conf')
        with self.tmpdir.join('conf', config).open("w") as file:
            for line in content:
                if line[0] == "config":
                    file.write("\n")  # Insert empty line
                else:
                    file.write("\t")  # Insert tabulator in front
                file.write("{} {}".format(line[0], line[1]))
                if len(line) > 2:
                    file.write(" '{}'".format(line[2]))
                file.write("\n")
            file.write("\n")

    def get(self, config):
        result = ()
        with self.tmpdir.join('conf', config).open() as file:
            for line in file.readlines():
                if not line or line.isspace():
                    continue
                values = line.strip().split(maxsplit=2)
                if len(values) > 2:
                    values[2] = values[2][1:-1]  # Strip ''
                result += (tuple(values),)
        return result

    def get_save(self, config):
        result = ()
        with self.tmpdir.join('save', config).open() as file:
            for line in file.readlines():
                if not line or line.isspace():
                    continue
                option, value = line.strip().split('=', 1)
                value = value[1:-1]  # Strip ''
                result += ((option, value),)
        return result

    def _safemkdir(self, directory):
        pth = self.tmpdir.join(directory).strpath
        if not os.path.isdir(pth):
            os.mkdir(pth)
        return pth

    def confdir(self):
        return self._safemkdir('conf')

    def savedir(self):
        return self._safemkdir('save')


class FakeUciSetup(UciSetup):
    """Class implementing backend access to fake uci backend.
    """

    def __init__(self, fake_uci):
        self.fake_uci = fake_uci

    def set(self, config, content):
        raise NotImplementedError

    def get(self, config):
        raise NotImplementedError

    def get_save(self, config):
        raise NotImplementedError

    def confdir(self):
        return os.path.devnull

    def savedir(self):
        return os.path.devnull


@pytest.fixture
def uci_setup(request, tmpdir, fake_uci):
    """Handle for interface implementing setup for uci configuration.
    """
    if request.config.getoption("-M"):
        return FakeUciSetup(fake_uci)
    return RealUciSetup(tmpdir)
