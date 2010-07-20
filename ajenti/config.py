from ConfigParser import ConfigParser

from ajenti.utils import detect_platform


class Config(ConfigParser):
    internal = {}
    filename = ''
    
    def __init__(self):
        ConfigParser.__init__(self)
        self.add_section('ajenti')
        self.set('ajenti', 'platform', detect_platform())
        
    def load(self, fn):
        self.filename = fn
        self.read(fn)

    def save(self):
        with open(self.filename, 'w') as f:
            self.write(f)
                           
    def get(self, val, *args):
        if len(args) == 0:
            return self.internal[val]
        else:
            return ConfigParser.get(self, val, args[0])

    def set(self, val, value, *args):
        if len(args) == 0:
            self.internal[val] = value
        else:
            if not self.has_section(val):
                self.add_section(val)
            ConfigParser.set(self, val, value, args[0])

    def has_option(self, sec, name):
        if not self.has_section(sec):
            self.add_section(sec)
        return ConfigParser.has_option(self, sec, name)
    
# class Config

