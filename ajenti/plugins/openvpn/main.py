import time

from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder

from backend import OpenVPNBackend


class State (object):
    pass


class Client (object):
    pass


class Message (object):
    pass


@plugin
class OpenVPN (SectionPlugin):
    def init(self):
        self.title = _('OpenVPN')
        self.icon = 'globe'
        self.category = _('Software')

        self.append(self.ui.inflate('openvpn:main'))

        def disconnect(u, c):
            try:
                self.backend.killbyaddr(u.raddress)
                time.sleep(1)
            except Exception as e:
                self.context.notify('error', e.message)
            self.refresh()

        self.find('clients').delete_item = disconnect

        self.binder = Binder(None, self)
        self.backend = OpenVPNBackend.get()

    def on_page_load(self):
        self.refresh()

    @on('hard-restart', 'click')
    def on_hard_restart(self):
        self.backend.restarthard()
        time.sleep(2)

    @on('soft-restart', 'click')
    def on_soft_restart(self):
        self.backend.restartcond()
        time.sleep(2)

    def refresh(self):
        try:
            self.backend.setup()
        except Exception as e:
            self.context.notify('error', e.message)
            self.context.launch('configure-plugin', plugin=self.backend)
            return

        self.state = State()

        try:
            self.backend.connect()
            self.state.stats = self.backend.getstats()
            self.state.status = self.backend.getstatus()
            self.state.messages = []
            self.state.clients = []
            for d in self.state.status['clients']:
                c = Client()
                c.__dict__.update(d)
                self.state.clients.append(c)
            for d in self.backend.getmessages():
                m = Message()
                m.timestamp, m.flags, m.text = d[:3]
                self.state.messages.append(m)

        except Exception as e:
            self.context.notify('error', e.message)

        self.binder.setup(self.state).populate()
