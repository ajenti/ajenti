from ajenti.api import *
from ajenti.ui.binder import Binder
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.util import platform_select

from reconfigure.configs import SupervisorConfig
from reconfigure.items.supervisor import ProgramData

from client import SupervisorServiceManager


@plugin
class Supervisor (SectionPlugin):
    def init(self):
        self.title = 'Supervisor'
        self.icon = 'play'
        self.category = _('Software')
        self.append(self.ui.inflate('supervisor:main'))
        self.mgr = SupervisorServiceManager.get()
        self.binder = Binder(None, self.find('main'))
        self.find('programs').new_item = lambda c: ProgramData()
        self.config = SupervisorConfig(path=platform_select(
            default='/etc/supervisor/supervisord.conf',
            centos='/etc/supervisord.conf',
        ))
        self.find('servicebar').name = platform_select(
            centos='supervisord',
            default='supervisor',
        )
        self.find('servicebar').reload()

    def on_page_load(self):
        self.refresh()

    def refresh(self):
        self.config.load()
        self.mgr.fill(self.config.tree.programs)
        self.binder.setup(self.config.tree).populate()

    @on('save', 'click')
    def on_save(self):
        self.binder.update()
        self.config.save()
        self.refresh()
