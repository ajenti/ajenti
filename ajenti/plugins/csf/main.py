import os
import subprocess

from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder

from reconfigure.configs import CSFConfig
from reconfigure.items.hosts import AliasData, HostData


@plugin
class CSFSection (SectionPlugin):
    def init(self):
        self.title = _('CSF Firewall')
        self.icon = 'fire'
        self.category = _('System')
        self.backend = CSFBackend.get()

        self.append(self.ui.inflate('csf:main'))

        self.config = CSFConfig(path='/etc/csf/csf.conf')
        self.list_allow = []
        self.list_deny = []
        self.list_tempallow = []
        self.list_tempban = []

        def delete_rule(csf_option, i):
            self.save()
            subprocess.call(['csf', csf_option, i.value.split('#')[0]])
            self.refresh()

        self.find('list_allow').on_delete = lambda i, c: delete('-ar', i)
        self.find('list_deny').on_delete = lambda i, c: delete('-dr', i)
        self.find('list_tempallow').on_delete = lambda i, c: delete('-tr', i)
        self.find('list_tempban').on_delete = lambda i, c: delete('-tr', i)

        def add_rule(csf_option, address):
            self.save()
            p = subprocess.Popen(['csf', csf_option, address], stdout=subprocess.PIPE)
            o, e = p.communicate()
            self.context.notify('info', o)
            self.refresh()

        self.find('list_allow-add').on('click', lambda: add_rule('-a', self.find('permanent-lists-add-address').value))
        self.find('list_deny-add').on('click', lambda: add_rule('-d', self.find('permanent-lists-add-address').value))
        self.find('list_tempallow-add').on('click', lambda: add_rule('-ta', self.find('temporary-lists-add-address').value))
        self.find('list_tempban-add').on('click', lambda: add_rule('-td', self.find('temporary-lists-add-address').value))

        self.binder = Binder(None, self)
        self.binder_lists = Binder(self, self.find('lists'))

    def on_page_load(self):
        self.refresh()

    def refresh(self):
        self.config.load()
        self.list_allow = self.backend.read_list('allow')
        self.list_deny = self.backend.read_list('deny')
        self.list_tempallow = self.backend.read_list('tempallow')
        self.list_tempban = self.backend.read_list('tempban')
        self.binder.setup(self.config.tree).populate()
        self.binder_lists.populate()

    @on('apply', 'click')
    def on_apply(self):
        self.backend.apply()
        self.context.notify('info', _('Applied'))

    @on('save', 'click')
    def save(self):
        self.binder.update()
        self.config.save()
        self.backend.write_list('allow', self.list_allow)
        self.backend.write_list('deny', self.list_deny)
        self.backend.write_list('tempallow', self.list_tempallow)
        self.backend.write_list('tempban', self.list_tempban)

        self.binder.setup(self.config.tree).populate()
        self.context.notify('info', _('Saved'))
        try:
            self.backend.test_config()
            self.context.notify('info', _('Self-test OK'))
        except Exception as e:
            self.context.notify('error', str(e))


class CSFListItem (object):
    def __init__(self, value):
        self.value = value


@plugin
@persistent
@rootcontext
class CSFBackend (object):
    csf_files = {
        'tempallow': '/var/lib/csf/csf.tempallow',
        'tempban': '/var/lib/csf/csf.tempban',
        'allow': '/etc/csf/csf.allow',
        'deny': '/etc/csf/csf.deny',
    }

    def apply(self):
        subprocess.call(['csf', '-r'])

    def test_config(self):
        p = subprocess.Popen(['/usr/local/csf/bin/csftest.pl'], stdout=subprocess.PIPE)
        o, e = p.communicate()
        if p.returncode != 0:
            raise Exception(e)

    def read_list(self, name):
        if not os.path.exists(self.csf_files[name]):
            return []
        return [
            CSFListItem(l.strip())
            for l in open(self.csf_files[name])
            if l.strip() and not l.startswith('#')
        ]

    def write_list(self, name, lst):
        open(self.csf_files[name], 'w').write(
            '\n'.join(
                x.value for x in lst
            ) + '\n'
        )
