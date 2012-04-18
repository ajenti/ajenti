# coding=utf-8
"""OpenVPN plugin backend"""
from ajenti.com import Plugin
from ajenti.utils.error import ConfigurationError
import manager

class OpenVPNBackend(Plugin):
    """
    OpenVPN plugin and widget backend
    @ivar _m: manager instance
    """
    icon = "/dl/openvpn/icon.png"
    text = "OpenVPN"

    def __init__(self, *args, **kwargs):
        """
        Initializes instance variables, creates manager instance and tests connection
        @return: Nothing
        """
        # Retrieve configuration settings
        addr = self.app.get_config(self).addr
        password = self.app.get_config(self).password
        if not addr:
            raise ConfigurationError("No address specified")
        # Check if addr is a "host:port" string
        (host, colon, port) = addr.partition(":")
        try:
            if colon:
                # IPv4/IPv6
                self._m = manager.manager(host = host, port = int(port), password = password)
            else:
                # UNIX Socket
                self._m = manager.manager(path = addr, password = password)
            # Test connection
            self.getpid()
        except Exception, e:
            raise ConfigurationError(str(e))

    def _execute(self, func, *args):
        """
        OpenVPN management interface is unable to handle more than one connection.
        This method is used to connect and disconnect (if was not connected manually) every
        time plugin wants to execute a command.
        @param func: Function to call
        @param args: Argument List
        @return: Function result
        """
        if not self._m.connected:
            self._m.connect()
            result = self._execute(func, *args)
            self._m.disconnect()
        else:
            result = func(*args)
        return result

    def connect(self):
        self._m.connect()

    def disconnect(self):
        self._m.disconnect()

    def getstatus(self):
        return self._execute(self._m.status)

    def getstats(self):
        return self._execute(self._m.stats)

    def killbyaddr(self, addr):
        return self._execute(self._m.killbyaddr, addr)

    def restartcond(self):
        return self._execute(self._m.signal, "SIGUSR1")

    def restarthard(self):
        return self._execute(self._m.signal, "SIGHUP")

    def getmessages(self):
        return self._execute(self._m.messages)

    def getpid(self):
        return self._execute(self._m.pid)