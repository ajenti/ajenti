# coding=utf-8
import os
import json
import logging
import subprocess

from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder

from templates import config_templates

config_dirs = {
    'main': '/etc/fail2ban/',
    'jails': '/etc/fail2ban/jail.d/',
    'actions': '/etc/fail2ban/action.d/',
    'filters': '/etc/fail2ban/filter.d/',
    'extra': '/etc/fail2ban/fail2ban.d/'
}

config_file_types = ('.conf', '.local')


# fail2ban:
#     configurations=
#             [
#                 f2b_configs:
#                     name=
#                     path=
#                     confillist=
#                         f2b_list:
#                             path=
#                             type=
#                             __list__=
#                                     f2b_config:
#                                         name=
#                                         configfile=
#                                         config=
#
#             ]


class f2b_Config(object):
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.configfile = os.path.join(path, name)
        self.config = ''

    def __repr__(self):
        return json.dumps({'name': self.name, 'configfile': self.configfile, 'config': self.config})

    def save(self):
        self.configfile = os.path.join(self.path, self.name)
        try:
            open(self.configfile, 'w').write(self.config)
            return self
        except IOError as e:
            logging.error(e.message)

    def update(self):
        self.configfile = os.path.join(self.path, self.name)
        self.config = ''.join((open(self.configfile).readlines()))
        return self


class f2b_Configs(object):
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.configlist = f2b_list(path=path, type=name)
        self.configlist.path = self.path

    def update(self):
        for filename in os.listdir(self.path):
            try:
                cf = os.path.join(self.path, filename)
                if os.path.isfile(cf) and (os.path.splitext(filename)[-1] in config_file_types):
                    self.configlist.append(f2b_Config(filename, self.path).update())
            except IOError as e:
                logging.error('Error reading file {0} in {1}.'.format(filename, self.path))
        self.configlist.sort(key=lambda k: k.name)
        return self


class f2b_list(list):
    def __init__(self, path='', type=''):
        self.path = path
        self.type = type


@plugin
class fail2ban(SectionPlugin):
    def init(self):
        self.title = 'fail2ban'
        self.icon = 'shield'
        self.category = _('Software')
        self.f2b_v = subprocess.check_output(['fail2ban-client', '--version']).splitlines()[0]
        self.append(self.ui.inflate('fail2ban:main'))
        self.binder = Binder(self, self)
        self.update_status = True

        def on_config_update(o, c, config, u):
            if config.__old_name != config.name:
                if os.path.exists(os.path.join(c.path, config.name)):
                    self.context.notify('error', _(
                        'File with name {0} already exists in {1}.').format(config.name, c.path))
                    self.update_status = False
                    config.name = config.__old_name
                    return
                logging.debug('renamed config file %s to %s' % (config.__old_name, config.name))
                os.unlink(config.configfile)
            config.save()
            self.update_status = True

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
                logging.debug('add config %s' % filename)
                conf = f2b_Config(s_fn, c.path)
                conf.config = config_templates[c.type]
                return conf.save()
            except IOError as e:
                print('Error writing file {0} in {1}'.format(filename, c.path))

        def delete_config(config, c):
            filename = config.configfile
            logging.debug('removed config %s' % config.configfile)
            c.remove(config)
            os.unlink(filename)

        self.find('configlist').post_item_update = on_config_update
        self.find('configlist').post_item_bind = on_config_bind
        self.find('configlist').new_item = new_config
        self.find('configlist').delete_item = delete_config

    def on_page_load(self):
        self.refresh()

    def refresh(self):
        self.configurations = [
            f2b_Configs(k, d).update()
            for k, d in config_dirs.iteritems()
            if os.path.isdir(d)
        ]
        self.binder.setup(self).populate()

    @on('save-button', 'click')
    def save(self):
        self.binder.update()
        if self.update_status:
            self.context.notify('info', _('Saved'))
        self.update_status = True
        self.binder.setup(self).populate()

    @on('check-regex', 'click')
    def check_regex(self):
        self.find('check-status').text = ''
        log_fname = self.find('log-filename').value
        filter_fname = self.find('filter-filename').value
        log_as_text = self.find('log-file').value
        filter_as_text = self.find('filter-file').value
        if not (log_fname or log_as_text) or not (filter_fname or filter_as_text):
            logging.debug('Filter checker. Some parameters are empty.')
            self.context.notify('error', _('Some parameters are empty.'))
            return

        with open(filter_fname + '.tmp', 'w') as rt:
            rt.write(self.find('filter-file').value)
            rt_name = rt.name
            rt.close()

        p = subprocess.Popen(['fail2ban-regex', '--full-traceback', log_fname, rt_name], stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        out, err = p.communicate()
        self.find('check-status').text = out

        os.unlink(rt_name)

    @on('open-filter-button', 'click')
    def open_filter(self):
        self.find('openfilterdialog').show()

    @on('openfilterdialog', 'button')
    def on_open_filter_dialog(self, button):
        self.find('openfilterdialog').visible = False

    @on('openfilterdialog', 'select')
    def on_filter_file_select(self, path=None):
        if not path:
            return
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
        if not path:
            return
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
