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
        self.binder = Binder(None, self)

    def on_page_load(self):
        self.config.load()
        self.binder.setup(self.config.tree).populate()

    @on('apply', 'click')
    def on_apply(self):
        self.backend.apply()
        self.context.notify('info', _('Applied'))

    @on('save', 'click')
    def save(self):
        self.binder.update()
        self.config.save()
        self.binder.setup(self.config.tree).populate()
        self.context.notify('info', _('Saved'))
        try:
            self.backend.test_config()
            self.context.notify('info', _('Self-test OK'))
        except Exception, e:
            self.context.notify('error', str(e))


@plugin
@persistent
@rootcontext
class CSFBackend (object):
    def apply(self):
        subprocess.call(['csf', '-r'])

    def test_config(self):
        p = subprocess.Popen(['/usr/local/csf/bin/csftest.pl'], stdout=subprocess.PIPE)
        o, e = p.communicate()
        if p.returncode != 0:
            raise Exception(e)
