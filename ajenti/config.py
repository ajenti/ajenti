from ConfigParser import ConfigParser
import os

from ajenti.utils import detect_platform


class Config(ConfigParser):
    internal = {}
    filename = ''
    proxies = {}

    def __init__(self):
        ConfigParser.__init__(self)
        self.set('platform', detect_platform()) # TODO: move this out

    def load(self, fn):
        self.filename = fn
        self.read(fn)

    def save(self):
        with open(self.filename, 'w') as f:
            self.write(f)

    def get_proxy(self, user):
        if not user in self.proxies:
            self.proxies[user] = ConfigProxy(self, user)
        return self.proxies[user]

    def get(self, section, val=None, default=None):
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
        if value is None:
            self.internal[section] = val
        else:
            if not self.has_section(section):
                self.add_section(section)
            ConfigParser.set(self, section, val, value)

    def has_option(self, sec, name):
        try:
            return ConfigParser.has_option(self, sec, name)
        except:
            return False


class ConfigProxy:
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
        if self.user is not None and self.cfg.has_option(section, val):
            return self.cfg.get(section, val)
        else:
            return self.base.get(section, val, default)

    def set(self, section, val, value=None):
        if self.user is None:
            raise Exception('Cannot modify anonymous config')
        self.cfg.set(section, val, value)

    def has_option(self, section, name):
        if self.base.has_option(section, name):
            return True
        if self.user is None:
            return False
        return self.cfg.has_option(section, name)

    def save(self):
        self.cfg.save()

    def options(self, section):
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
        try:
            self.cfg.remove_option(section, val)
        except:
            return False
