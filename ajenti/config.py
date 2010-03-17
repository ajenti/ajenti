from ConfigParser import ConfigParser

from ajenti.utils import detect_platform

default_values = {
                    'bind_host': '',
                    'bind_port': '8000'
                 }

default_values['platform'] = detect_platform()

class Config(ConfigParser):
    internal = {}
    def __init__(self):
        ConfigParser.__init__(self, default_values)
        # Add default configuration section, 
        # which could be overrided in config file
        self.add_section('ajenti')

    def get(self, val, *args):
        if len(args) == 0:
            return self.internal[val]
        else:
            return ConfigParser.get(self, val, args[0])

    def set(self, val, value, *args):
        if len(args) == 0:
            self.internal[val] = value
        else:
            ConfigParser.set(self, val, value, args[0])

# class Config

