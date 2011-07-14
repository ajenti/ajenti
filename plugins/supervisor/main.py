from ajenti.ui import *
from ajenti.com import implements
from ajenti.api import *
from ajenti.utils import *
from ajenti import apis

from client import SVClient


class SVPlugin(CategoryPlugin):
    text = 'Supervisor'
    icon = '/dl/supervisor/icon.png'
    folder = 'apps'

    def on_session_start(self):
        self._client = SVClient(self.app)
        self._tail = None

    def get_ui(self):
        ui = self.app.inflate('supervisor:main')

        if not self._client.test():
            raise ConfigurationError('Please check supervisorctl configuration')

        for x in self._client.status():
            ui.append('list', UI.DataTableRow(
                UI.Label(text=x['name']),
                UI.Label(text=x['status']),
                UI.Label(text=x['info']),
                UI.HContainer(
                    UI.MiniButton(
                        id='start/'+x['name'],
                        text='Start',
                    ) if x['status'] != 'RUNNING' else None,
                    UI.MiniButton(
                        id='restart/'+x['name'],
                        text='Restart',
                    ) if x['status'] == 'RUNNING' else None,
                    UI.MiniButton(
                        id='stop/'+x['name'],
                        text='Stop',
                    ) if x['status'] == 'RUNNING' else None,
                    UI.MiniButton(
                        id='tail/'+x['name'],
                        text='Log tail',
                    )
                ),
            ))

        if self._tail is not None:
            ui.append('main', UI.CodeInputBox(
                value=self._client.tail(self._tail),
                hidecancel=True,
            ))


        return ui

    @event('minibutton/click')
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
