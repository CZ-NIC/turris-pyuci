# Copyright (c) 2019, CZ.NIC, z.s.p.o. (http://www.nic.cz/)
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the CZ.NIC nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL CZ.NIC BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from uci import Uci, UciExceptionNotFound


class EUci(Uci):
    """Extended Uci wrapper
    """
    __BOOLEAN_VALUES = {
        "0": False,
        "no": False,
        "off": False,
        "false": False,
        "disabled": False,
        "1": True,
        "yes": True,
        "on": True,
        "true": True,
        "enabled": True,
    }
    __BOOLEAN_TRUE = "1"
    __BOOLEAN_FALSE = "0"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_default(self, *args, default=None, **kwargs):
        """Wrap UCI get method with additional check for missing config value.
        Returns default value if config value cannot be found.
        """
        try:
            return self.get(*args, **kwargs)
        except UciExceptionNotFound:
            return default

    def get_boolean(self, *args, **kwargs):
        """Returns given UCI config as a boolean.
        Value '0', 'no', 'off', 'false' or 'disabled' is returned as False.
        Value '1' , 'yes', 'on', 'true' or 'enabled' is returned as True.
        ValueError is raised on any other value.
        """
        value = self.get(*args, **kwargs)
        if value.lower() not in self.__BOOLEAN_VALUES:
            raise ValueError
        return self.__BOOLEAN_VALUES[value.lower()]

    def get_boolean_default(self, *args, default=False, **kwargs):
        """Returns given UCI config as a boolean.
        Value '0', 'no', 'off', 'false' or 'disabled' is returned as False.
        Value '1' , 'yes', 'on', 'true' or 'enabled' is returned as True.
        ValueError is raised on any other value.
        Returns default value as bool if config value cannot be found.
        """
        try:
            return self.get_boolean(*args, **kwargs)
        except UciExceptionNotFound:
            return bool(default)

    def set_boolean(self, *args):
        """Sets boolean value to given UCI config.
        """
        self.set(*(args[:-1]), self.__BOOLEAN_TRUE if args[-1] else self.__BOOLEAN_FALSE)

    def get_integer(self, *args, **kwargs):
        """Returns given UCI config as an integer.
        Raises ValueError if config value can't be converted to int.
        """
        return int(self.get(*args, **kwargs))

    def get_integer_default(self, *args, default=0, **kwargs):
        """Returns given UCI config as an integer.
        Raises ValueError if config value can't be converted to int.
        Returns default value as int if config value cannot be found.
        """
        try:
            return self.get_integer(*args, **kwargs)
        except UciExceptionNotFound:
            return int(default)

    def set_integer(self, *args):
        """Sets integer to given UCI config.
        """
        self.set(*(args[:-1]), str(args[-1]))
