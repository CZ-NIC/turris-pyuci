"""Unified configuration interface bindings
"""
import os
import string
import random
import collections

current_state = None


class Uci():
    """Top level entry point to uci context. Create instance of this for any
    uci access
    """
    _ANONYM_CONF_LEN = 6

    def __init__(self, savedir=None, confdir=None):
        self._anonym_sections = set()
        self._tainted = False
        self.set_savedir("/tmp/.uci" if savedir is None else savedir)
        self.set_confdir("/etc/config" if confdir is None else confdir)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if self._tainted:
            for config in self.list_configs():
                self.commit(config)

    def _anonym_section_name(self):
        """Generates new name for anonymous sections.
        """
        value = ''.join(random.choices(string.ascii_lowercase + string.digits, k=self._ANONYM_CONF_LEN))
        if value in self._anonym_sections:
            return self._anonym_section_name()
        self._anonym_sections.add(value)
        return "cfg" + value

    def _get(self, section_value, *args):
        argc = len(args)
        if argc == 1:
            # TODO go trough all sections in config
            raise NotImplementedError
        if args == 2:
            if section_value:
                path = self._path(*args)
            else:
                # TODO go trough all options and lists
                raise NotImplementedError

    def _path(self, *args):
        """Generic convertor from arguments to dot separated path"""
        raise NotImplementedError

    def get(self, *args):
        """Get value"""
        return self._get(True, *args)

    def get_all(self, *args):
        """Get all values even for sections"""
        return self._get(False, *args)

    def set(self, *args):
        """Set value"""
        current_state[self._savedir][self._path(*args[:-1])] = str(args[-1])
        self._tainted = True

    def delete(self, *args):
        """Delete option"""
        path = self._path(*args)
        ucidir = current_state[self._savedir]
        if path in ucidir:
            del ucidir[path]
            self._tainted = True

    def add(self, *args):
        """Add new anonymous section"""
        # This is not implemented in pyuci yet.
        self._tainted = True
        raise NotImplementedError

    def rename(self, *args):
        """Rename an element"""
        path = self._path(*args)
        ucidir = current_state[self._savedir]
        if path in ucidir:
            ucidir[path] = ucidir.pop(path)
            self._tainted = True

    def reorder(self, *args):
        self._tainted = True
        raise NotImplementedError

    def save(self, *args):
        raise NotImplementedError

    def commit(self, *args):
        self._tainted = False
        raise NotImplementedError

    def revert(self, *args):
        self._tainted = False
        raise NotImplementedError

    def unload(self, *args):
        # This is not implemented in pyuci yet.
        raise NotImplementedError

    def load(self, *args):
        # This is not implemented in pyuci yet.
        raise NotImplementedError

    def changes(self, *args):
        # This is not implemented in pyuci yet.
        raise NotImplementedError

    def list_configs(self):
        raise NotImplementedError

    def confdir(self):
        return self._confdir

    def set_confdir(self, path):
        self._confdir = os.path.normpath(path).rstrip('/')

    def savedir(self):
        return self._savedir

    def set_savedir(self, path):
        self._savedir = os.path.normpath(path).rstrip('/')


class UciException(Exception):
    pass


class UciExceptionNotFound(UciException):
    pass
