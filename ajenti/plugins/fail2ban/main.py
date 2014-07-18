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
        return json.dumps({'name': self.name, 'configfile': self.configfile, 'config': self.config})

    def save(self):
        try:
            open(self.configfile, 'w').write(self.config)
        except IOError as e:
            logging.error(e.message)


class f2b_Configs(object):
    def __init__(self, name, path, configlist):
        self.name = name
        self.path = path
        self.configlist = configlist if isinstance(configlist, list) else []


class f2b_list(list):
    def __init__(self):
        self.path = ''


def listing_of_configs(path):
    configs = f2b_list()
    configs.path = path
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

        self.configurations = [f2b_Configs(x, config_dirs[x], listing_of_configs(config_dirs[x])) for x in
                               config_dirs.keys()]

        self.append(self.ui.inflate('fail2ban:main'))
        self.binder = Binder(self, self)

        def on_config_update(o, c, config, u):
            # if config.__old_name != config.name:
            # self.log('renamed config file %s to %s' % (config.__old_name, config.name))
            #    self.hosts_dir.rename(config.__old_name, config.name)
            config.save()

        def on_config_bind(o, c, config, u):
            config.__old_name = config.name

        def new_config(c):
            new_fn = 'untitled{0}.conf'
            s_fn = new_fn.format('')
            filename = os.path.join(c.path, s_fn)
            i = 1
            while os.path.isfile(filename) or os.path.isdir(filename):
                s_fn = new_fn.format('_' + str(i))
                filename = os.path.join(c.path, s_fn)
                i += 1
            try:
                open(filename, 'w').write(' ')
                logging.info('add config %s' % filename)
                return f2b_Config(s_fn, filename, '')
            except IOError as e:
                print('Error writing file {0} in {1}'.format(filename, c.path))

        def delete_config(config, c):
            filename = config.configfile
            logging.info('removed config %s' % config.configfile)
            c.remove(config)
            os.unlink(filename)

        self.find('configlist').post_item_update = on_config_update
        self.find('configlist').post_item_bind = on_config_bind
        self.find('configlist').new_item = new_config
        self.find('configlist').delete_item = delete_config


    def on_page_load(self):
        self.refresh()

    def refresh(self):
        self.configurations = [f2b_Configs(x, config_dirs[x], listing_of_configs(config_dirs[x])) for x in
                               config_dirs.keys()]
        self.binder.populate()

    @on('save-button', 'click')
    def save(self):
        self.binder.update()
        self.context.notify('info', 'Saved')
