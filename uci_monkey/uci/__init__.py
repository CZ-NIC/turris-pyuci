"""Unified configuration interface bindings
"""
import threading

_state = None
_state_lock = threading.Lock()


class Uci():
    """Top level entry point to uci context. Create instance of this for any
    uci access
    """

    def __init__(self, savedir=None, confdir=None):
        self.tainted = False

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if self.tainted:
            for config in self.list_configs():
                self.commit(config)

    def get(self, *args):
        raise NotImplementedError

    def get_all(self, *args):
        raise NotImplementedError

    def set(self, *args):
        self.tainted = True
        raise NotImplementedError

    def delete(self, *args):
        self.tainted = True
        raise NotImplementedError

    def add(self, *args):
        self.tainted = True
        raise NotImplementedError

    def rename(self, *args):
        self.tainted = True
        raise NotImplementedError

    def reorder(self, *args):
        self.tainted = True
        raise NotImplementedError

    def save(self, *args):
        raise NotImplementedError

    def commit(self, *args):
        raise NotImplementedError
        self.tainted = False

    def revert(self, *args):
        raise NotImplementedError
        self.tainted = False

    def unload(self, *args):
        raise NotImplementedError

    def load(self, *args):
        raise NotImplementedError

    def changes(self, *args):
        raise NotImplementedError

    def list_configs(self):
        raise NotImplementedError

    def confdir(self):
        raise NotImplementedError

    def set_confdir(self, path):
        raise NotImplementedError

    def savedir(self):
        raise NotImplementedError

    def set_savedir(self, path):
        raise NotImplementedError


class UciException(Exception):
    pass


class UciExceptionNotFound(UciException):
    pass
