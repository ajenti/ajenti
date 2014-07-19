# coding=utf-8
import os, json, logging, tempfile, time

import subprocess

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


@plugin
class f2b_Config(BasePlugin):
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
            self.context.notify('error', _('Could not save config file. %s') % str(e))
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
                configs.append(f2b_Config.new(filename, cf, open(cf).readlines()))
        except IOError as e:
            print('Error reading file {0} in {1}'.format(filename, path))
    return configs


@plugin
class fail2ban(SectionPlugin):
    def init(self):
        self.title = 'fail2ban'
        self.icon = 'shield'
        self.category = _('Software')
        self.f2b_v = subprocess.check_output(['fail2ban-client', '--version']).splitlines()[0]
        self.append(self.ui.inflate('fail2ban:main'))
        self.binder = Binder(self, self)

        def on_config_update(o, c, config, u):
            # if config.__old_name != config.name:
            # self.log('renamed config file %s to %s' % (config.__old_name, config.name))
            # self.hosts_dir.rename(config.__old_name, config.name)
            config.save()

        def on_config_bind(o, c, config, u):
            config.__old_name = config.name

        def new_config(c):
            new_fn = 'untitled{0}.conf'
            s_fn = new_fn.format('')
            filename = os.path.join(c.path, s_fn)
            i = 1
            while os.path.exists(filename):
                s_fn = new_fn.format('_' + str(i))
                filename = os.path.join(c.path, s_fn)
                i += 1
            try:
                open(filename, 'w').write(' ')
                logging.info('add config %s' % filename)
                return f2b_Config.new(s_fn, filename, '')
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
        self.find('f2b_v').text = self.f2b_v
        self.refresh()

    def refresh(self):
        self.configurations = [
            f2b_Configs(k, d, listing_of_configs(d))
            for k, d in config_dirs.iteritems()
            if os.path.isdir(d)
        ]
        self.binder.setup(self).populate()

    @on('save-button', 'click')
    def save(self):
        self.binder.update()
        self.context.notify('info', 'Saved')

    @on('check-regex', 'click')
    def check_regex(self):
        log_fname = self.find('log-filename').value
        filter_fname = self.find('filter-filename').value
        log_as_text = self.find('log-file').value
        filter_as_text = self.find('filter-file').value
        if not (log_fname or log_as_text) or not (filter_fname or filter_as_text):
            logging.info('Filter checker. Some parametrs empty.')
            self.context.notify('Some parametrs empty.')
            return

        with tempfile.NamedTemporaryFile(delete=False) as lt:
            lt.write(self.find('log-file').value)
            lt_name = lt.name
        with tempfile.NamedTemporaryFile(delete=False) as rt:
            rt.write(self.find('filter-file').value)
            rt_name = rt.name

        p = subprocess.Popen(['fail2ban-regex', lt_name, rt_name], stdout=subprocess.PIPE, universal_newlines=True)
        out, err = p.communicate()
        self.find('check-status').text = out

        os.unlink(rt_name)
        os.unlink(lt_name)

    @on('open-filter-button', 'click')
    def open_filter(self):
        self.find('openfilterdialog').show()

    @on('openfilterdialog', 'button')
    def on_open_filter_dialog(self, button):
        self.find('openfilterdialog').visible = False

    @on('openfilterdialog', 'select')
    def on_filter_file_select(self, path=None):
        self.find('openfilterdialog').visible = False
        self.find('filter-filename').value = path
        self.find('filter-file').value = ''.join(open(path).readlines())


    @on('open-log-button', 'click')
    def open_log(self):
        self.find('openlogdialog').show()

    @on('openlogdialog', 'button')
    def on_open_log_dialog(self, button):
        self.find('openlogdialog').visible = False

    @on('openlogdialog', 'select')
    def on_log_file_select(self, path=None):
        self.find('openlogdialog').visible = False
        self.find('log-filename').value = path
        self.find('log-file').value = ''.join(open(path).readlines())

    @on('save-filter-button', 'click')
    def save_filter(self):
        try:
            open(self.find('filter-filename').value, 'w').write(self.find('filter-file').value)
        except IOError as e:
            self.context.notify('error', _('Could not save config file. %s') % str(e))
            logging.error(e.message)
