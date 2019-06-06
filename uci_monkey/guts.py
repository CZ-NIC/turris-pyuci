"""These are abstraction for building and managing uci_monkey internal
configuration representation.
"""
import re
import collections
import threading


class UciDir:
    """UCI configuration state. It allows you to overly and in general
    manage current UCI configuration. Just instanciate it to create new state
    overlay. To drop it you call drop().
    Note that states automatically create linked-list chain.
    """
    # Internal structure of conf:

    def __init__(self):
        self.conf = collections.OrderedDict()

    def __validate_key(self, key):
        pkey = key.split('.')
        if not 2 <= len(pkey) <= 3:
            raise InvalidUciSpecException("Only allowed keys are of form: config.section[.option]")
        if not self._re_option.fullmatch(pkey[0]):
            raise InvalidUciSpecException("Section 'config' does not conform to appropriate format")
        if not self._re_section.fullmatch(pkey[1]):
            raise InvalidUciSpecException("Section 'section' does not conform to appropriate format")
        if len(pkey) == 3 and not self._re_option.fullmatch(pkey[2]):
            raise InvalidUciSpecException("Section 'option' does not conform to appropriate format")
        return pkey

    def __getitem__(self, key):
        # TODO
        pass

    def __setitem__(self, key, value):
        pkey = self.__validate_key(key)
        if len(pkey) == 3 and isinstance(value, collections.Iterable) and not isinstance(value, str):
            pass

    def __delitem__(self, key):
        # TODO
        pass

    def iterfilter(self, key):
        """Returns generator to go trough all subsequent sections"""
        returned = set()
        for kkey in self:
            if kkey.startswith(key + '.'):
                kkey_tail = kkey[len(key) + 1:]  # TODO strip rest
                returned.add(kkey_tail)
                yield kkey_tail

    def sections(self, config, type):
        """Generator to iterate over all sections of given type"""
        raise NotImplementedError

    def sort(self):
        """Resort current content (sections in configs)"""
        raise NotImplementedError

    def section_move(self, config, section, position):
        """Move specified section to more appropriate place"""
        raise NotImplementedError

    def merge(dir: UciDir):
        """Merge other UciDir instance to this one.
        """
        raise NotImplementedError


class UciState(dict):
    """UCI configuration state. It allows you to overly and in general manage current UCI configuration. Just
    instanciate it to create new state overlay. To drop it you call drop().
    """

    def __setitem__(self, path, value):
        if not isinstance(value, UciDir):
            raise TypeError("'{}' is not of UciDir instance".format(type(value)))
        super().__setitem__(path, list(value))

    def __missing__(self, key):
        self[key] = UciDir()
        return self[key]

    def conf(self):
        """Returns default directory for confdir."""
        return self["/etc/config"]

    def save(self):
        """Returns default directory for savedir."""
        return self["/tmp/.uci"]


class InvalidUciSpecException(Exception):
    """Provided UCI config.section.option specifier is invalid.
    """
