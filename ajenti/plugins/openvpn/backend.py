# coding=utf-8
from ajenti.api import plugin, BasePlugin
from ajenti.plugins.configurator.api import ClassConfigEditor

import manager


@plugin
class OpenVPNClassConfigEditor (ClassConfigEditor):
    title = 'OpenVPN'
    icon = 'globe'

    def init(self):
        self.append(self.ui.inflate('openvpn:config'))


@plugin
class OpenVPNBackend (BasePlugin):
    """
    OpenVPN plugin and widget backend
    @ivar _m: manager instance
    """
    default_classconfig = {'addr': '', 'password': ''}
    classconfig_editor = OpenVPNClassConfigEditor

    def setup(self):
        """
        Initializes instance variables, creates manager instance and tests connection
        @return: Nothing
        """
        # Retrieve configuration settings
        addr = self.classconfig['addr']
        password = self.classconfig['password']
        if not addr:
            raise Exception('No address specified')
        # Check if addr is a "host:port" string
        (host, colon, port) = addr.partition(":")
        try:
            if colon:
                # IPv4/IPv6
                self._m = manager.manager(host=host, port=int(port), password=password)
            else:
                # UNIX Socket
                self._m = manager.manager(path=addr, password=password)
            # Test connection
            self.getpid()
        except Exception, e:
            raise Exception(str(e))

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
