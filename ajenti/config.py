"""
Tools for manipulating Ajenti configuration files
"""

__all__ = ['Config', 'ConfigProxy']

from ConfigParser import ConfigParser
import os

from ajenti.utils import detect_platform


class Config(ConfigParser):
    """
    A wrapper around ConfigParser
    """
    internal = {}
    filename = ''
    proxies = {}

    def __init__(self):
        ConfigParser.__init__(self)
        self.set('platform', detect_platform()) # TODO: move this out

    def load(self, fn):
        """
        Loads configuration data from the specified file
        :param  fn:     Config file path
        :type   fn:     str
        """
        self.filename = fn
        self.read(fn)

    def save(self):
        """
        Saves data to the last loaded file
        """
        with open(self.filename, 'w') as f:
            self.write(f)

    def get_proxy(self, user):
        """
        :param  user: User
        :type   user: str
        :returns:   :class:`ConfigProxy` for the specified :param:user
        """
        if not user in self.proxies:
            self.proxies[user] = ConfigProxy(self, user)
        return self.proxies[user]

    def get(self, section, val=None, default=None):
        """
        Gets a configuration parameter
        :param  section:    Config file section
        :type   section:    str
        :param  val:        Value name
        :type   val:        str
        :param  section:    Default value
        :type   section:    str
        :returns:           value or default value if value was not found
        """
        if val is None:
            return self.internal[section]
        else:
            try:
                return ConfigParser.get(self, section, val)
            except:
                if default is not None:
                    return default
                raise

    def set(self, section, val, value=None):
        """
        Sets a configuration parameter
        :param  section:    Config file section
        :type   section:    str
        :param  val:        Value name
        :type   val:        str
        :param  value:      Value
        :type   value:      str
        """
        if value is None:
            self.internal[section] = val
        else:
            if not self.has_section(section):
                self.add_section(section)
            ConfigParser.set(self, section, val, value)

    def has_option(self, section, name):
        """
        Checks if an parameter is present in the given section
        :param  section:    Config file section
        :type   section:    str
        :param  name:        Value name
        :type   name:        str
        :returns:           bool
        """
        try:
            return ConfigParser.has_option(self, section, name)
        except:
            return False


class ConfigProxy:
    """
    A proxy class that directs all writes into user's personal config file
    while reading from both personal and common configs.

    - *cfg* - :class:`Config` common for all users,
    - *user* - user name
    """

    def __init__(self, cfg, user):
        self.base = cfg
        self.user = user
        self.filename = None
        if user is None:
            return
        self.cfg = Config()
        path = os.path.split(self.base.filename)[0] + '/users/%s.conf'%user
        if not os.path.exists(path):
            open(path, 'w').close()
        self.filename = path
        self.cfg.load(path)

    def get(self, section, val=None, default=None):
        """
        Gets a configuration parameter
        :param  section:    Config file section
        :type   section:    str
        :param  val:        Value name
        :type   val:        str
        :param  section:    Default value
        :type   section:    str
        :returns:           value or default value if value was not found
        """
        if self.user is not None and self.cfg.has_option(section, val):
            return self.cfg.get(section, val)
        else:
            return self.base.get(section, val, default)

    def set(self, section, val, value=None):
        """
        Sets a configuration parameter
        :param  section:    Config file section
        :type   section:    str
        :param  val:        Value name
        :type   val:        str
        :param  value:      Value
        :type   value:      str
        """
        if self.user is None:
            raise Exception('Cannot modify anonymous config')
        self.cfg.set(section, val, value)

    def has_option(self, section, name):
        """
        Checks if a parameter is present in the given section
        :param  section:    Config file section
        :type   section:    str
        :param  name:        Value name
        :type   name:        str
        :returns:           bool
        """
        if self.base.has_option(section, name):
            return True
        if self.user is None:
            return False
        return self.cfg.has_option(section, name)

    def save(self):
        """
        Saves the config
        """
        self.cfg.save()

    def options(self, section):
        """
        Enumerates parameters in the given section
        :param  section:    Config file section
        :type   section:    str
        :returns:           list(str)
        """
        r = []
        try:
            r.extend(self.base.options(section))
        except:
            pass
        try:
            r.extend(self.cfg.options(section))
        except:
            pass
        return r

    def remove_option(self, section, val):
        """
        Removes a parameter from the given section
        :param  section:    Config file section
        :type   section:    str
        :param  val:        Value name
        :type   val:        str
        :returns:           False is there were no such parameter
        """
        try:
            self.cfg.remove_option(section, val)
        except:
            return False

    def remove_section(self, section):
        """
        Removes a section from the given section
        :param  section:    Config file section
        :type   section:    str
        :returns:           False is there were no such parameter
        """
        try:
            self.cfg.remove_section(section)
        except:
            return False
