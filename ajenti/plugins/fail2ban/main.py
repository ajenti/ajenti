# coding=utf-8
import os, json, logging

from ajenti.api import *
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
    def __init__(self, name, configfile, config):
        self.name = name
        self.configfile = configfile
        self.config = ''.join(config)

    def __repr__(self):
        return json.dumps({'name': self.name, 'configfile': self.configfile, 'configtext': self.config})

    def save(self):
        try:
            open(self.configfile, 'w').write(self.config)
        except IOError as e:
            logging.error(e.message)


class f2b_Configs(object):
    def __init__(self, name, configlist):
        self.name = name
        self.configlist = configlist if isinstance(configlist, list) else []

def listing_of_configs(path):
    configs = []
    for filename in os.listdir(path):
        try:
            cf = os.path.join(path, filename)
            if os.path.isfile(cf) and (os.path.splitext(filename)[-1] in config_file_types):
                configs.append(f2b_Config(filename, cf, open(cf, 'r').readlines()))
        except IOError as e:
            print('Error reading file {0} in {1}'.format(filename, path))
    return configs


@plugin
class fail2ban(SectionPlugin):
    def init(self):
        self.title = 'fail2ban'  # those are not class attributes and can be only set in or after init()
        self.icon = 'shield'
        self.category = _('Software')

        self.configurations = [f2b_Configs(x, listing_of_configs(config_dirs[x])) for x in config_dirs.keys()]

        self.append(self.ui.inflate('fail2ban:main'))
        self.binder = Binder(self, self)

        def on_config_update(o, c, config, u):
            if config.__old_name != config.name:
                self.log('renamed host %s to %s' % (config.__old_name, config.name))
                self.hosts_dir.rename(config.__old_name, config.name)
            config.save()

        def on_config_bind(o, c, config, u):
            config.__old_name = config.name

        self.find('configlist').post_item_update = on_config_update
        self.find('configlist').post_item_bind = on_config_bind


    def on_page_load(self):
        self.refresh()

    def refresh(self):
        self.configurations = [f2b_Configs(x, listing_of_configs(config_dirs[x])) for x in config_dirs.keys()]
        self.binder.update()
        self.binder.populate()

    @on('save-button', 'click')
    def save(self):
        self.binder.update()
        self.refresh()
        self.context.notify('info', 'Saved')