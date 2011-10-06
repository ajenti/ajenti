from ajenti.ui import *
from ajenti.com import implements
from ajenti.api import *
from ajenti.utils import *
from ajenti import apis

from client import SVClient


class SVPlugin(apis.services.ServiceControlPlugin):
    text = 'Supervisor'
    icon = '/dl/supervisor/icon.png'
    folder = 'apps'
    service_name = 'supervisor'

    def on_session_start(self):
        self._client = SVClient(self.app)
        self._tail = None

    def get_main_ui(self):
        ui = self.app.inflate('supervisor:main')

        if not self._client.test():
            raise ConfigurationError('Please check supervisorctl configuration')

        for x in self._client.status():
            ui.append('list', UI.DTR(
                UI.Label(text=x['name']),
                UI.Label(text=x['status']),
                UI.Label(text=x['info']),
                UI.HContainer(
                    UI.TipIcon(
                        id='start/'+x['name'],
                        text='Start',
                        icon='/dl/core/ui/stock/service-start.png',
                    ) if x['status'] != 'RUNNING' else None,
                    UI.TipIcon(
                        id='restart/'+x['name'],
                        text='Restart',
                        icon='/dl/core/ui/stock/service-restart.png',
                    ) if x['status'] == 'RUNNING' else None,
                    UI.TipIcon(
                        id='stop/'+x['name'],
                        text='Stop',
                        icon='/dl/core/ui/stock/service-stop.png',
                    ) if x['status'] == 'RUNNING' else None,
                    UI.TipIcon(
                        id='tail/'+x['name'],
                        text='Log tail',
                        icon='/dl/core/ui/stock/paste.png',
                    )
                ),
            ))

        if self._tail is not None:
            ui.append('main', UI.InputBox(
                value=self._client.tail(self._tail),
                hidecancel=True,
                extra='code',
            ))


        return ui

    @event('button/click')
    def on_button(self, event, params, vars=None):
        if params[0] == 'start':
            self._client.start(params[1])
        if params[0] == 'restart':
            self._client.restart(params[1])
        if params[0] == 'stop':
            self._client.stop(params[1])
        if params[0] == 'tail':
            self._tail = params[1]

    @event('dialog/submit')
    def on_submit(self, event, params, vars=None):
        self._tail = None
