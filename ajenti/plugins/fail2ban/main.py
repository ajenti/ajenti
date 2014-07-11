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


class f2b_Config(object):
    def __init__(self, name, configfile, configtext):
        self.name = name
        self.configfile = configfile
        self.configtext = configtext

    def __repr__(self):
        return json.dumps({'name': self.name, 'configfile': self.configfile, 'configtext': self.configtext})


class f2b_config_list(object):
    def __init__(self, name, config_list):
        self.name = name
        if config_list and type(config_list) is list:
            self.config_list = config_list
        else:
            self.config_list = []


def listing_of_configs():
    configs = []
    config_list = []
    for key, path in config_dirs.items():
        for filename in os.listdir(path):
            try:
                cf = os.path.join(path, filename)
                if os.path.isfile(cf) and ('.conf' or '.py' in os.path.splitext(filename)):
                    with open(cf, 'r') as f:
                        data = f.readlines()
                        configs.append(f2b_Config(filename, cf, data))
            except IOError as e:
                print('Error reading file {0} in {1}'.format(filename, path))
        config_list.append(f2b_config_list(key, configs))
    return config_list


@plugin
class fail2ban(SectionPlugin):
    def init(self):
        self.title = 'fail2ban'  # those are not class attributes and can be only set in or after init()
        self.icon = 'shield'
        self.category = _('Software')
        service_name = 'fail2ban'

        self.append(self.ui.inflate('fail2ban:main'))

        # This callback is used to autogenerate a new item with 'Add' button
        # self.find('collection').new_item = lambda c: f2b_Config(name='new config', configfile='', configtext='')

        # self.find('data').text = repr(self.obj_collection)
        self.configs = listing_of_configs()
        self.configs['jails']
        self.binder = Binder(self, self)
        self.refresh()

    def refresh(self):
        self.configs = listing_of_configs()
        self.binder.update()
        self.binder.populate()

    @on('apply', 'click')
    def on_apply(self):
        self.refresh()
