# coding=utf-8
import os, json

from ajenti.api import plugin
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder

config_dirs = {
    'main': '/etc/fail2ban/',
    'jails': '/etc/fail2ban/jail.d/',
    'actions': '/etc/fail2ban/action.d/',
    'filters': '/etc/fail2ban/filter.d/',
    'extra': '/etc/fail2ban/fail2ban.d/'
}

config_file_types = ('.conf', '.py', '.local')

class f2b_Config(object):
    def __init__(self, name, configfile, configtext):
        self.name = name
        self.configfile = configfile
        self.configtext = ''.join(configtext)

    def __repr__(self):
        return json.dumps({'name': self.name, 'configfile': self.configfile, 'configtext': self.configtext})



def listing_of_configs(name, path):
    configs = []
    for filename in os.listdir(path):
        try:
            cf = os.path.join(path, filename)
            if os.path.isfile(cf) and (os.path.splitext(filename) in config_file_types):
                with open(cf, 'r') as f:
                    data = f.readlines()
                    configs.append(f2b_Config(filename, cf, data))
        except IOError as e:
            print('Error reading file {0} in {1}'.format(filename, path))
    return configs



@plugin
class fail2ban(SectionPlugin):
    def init(self):
        self.title = 'fail2ban'  # those are not class attributes and can be only set in or after init()
        self.icon = 'shield'
        self.category = _('Software')
        service_name = 'fail2ban'
        self.main = listing_of_configs('main', config_dirs['main'])
        self.jails = listing_of_configs('jails', config_dirs['jails'])
        self.actions = listing_of_configs('actions', config_dirs['actions'])
        self.filters = listing_of_configs('filters', config_dirs['filters'])
        self.extra = listing_of_configs('extra', config_dirs['extra'])

        self.append(self.ui.inflate('fail2ban:main'))

        self.binder = Binder(self, self)
        self.refresh()

    def refresh(self):
        self.main = listing_of_configs('main', config_dirs['main'])
        self.jails = listing_of_configs('jails', config_dirs['jails'])
        self.actions = listing_of_configs('actions', config_dirs['actions'])
        self.filters = listing_of_configs('filters', config_dirs['filters'])
        self.extra = listing_of_configs('extra', config_dirs['extra'])
        self.binder.update()
        self.binder.populate()

    @on('apply', 'click')
    def on_apply(self):
        self.refresh()
