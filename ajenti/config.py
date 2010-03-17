from ConfigParser import ConfigParser

from ajenti.utils import detect_platform

default_values = {
                    'bind_host': '',
                    'bind_port': '8000'
                 }

default_values['platform'] = detect_platform()

class Config(ConfigParser):

    def __init__(self):
        ConfigParser.__init__(self, default_values)
        # Add default configuration section, 
        # which could be overrided in config file
        self.add_section('ajenti')

# class Config

