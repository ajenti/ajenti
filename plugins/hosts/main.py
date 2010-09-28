from ajenti.ui import *
from ajenti.app.helpers import *

import backend


class HostsPlugin(CategoryPlugin):
    text = 'Hosts'
    icon = '/dl/hosts/icon_small.png'
    folder = 'system'

    def on_init(self):
        self.hosts = backend.read()

    def on_session_start(self):
        self._log = ''
        self._editing = None

    def get_ui(self):
        panel = UI.PluginPanel(
                    UI.Label(text='The static lookup table for hostnames'), 
                    title='Hosts', 
                    icon='/dl/hosts/icon.png'
                )

        t = UI.DataTable(UI.DataTableRow(
            UI.Label(text='IP address'),
            UI.Label(text='Hostname'),
            UI.Label(text='Aliases'),
            UI.Label(),
            header = True
        ))
        for h in self.hosts:
            t.append(UI.DataTableRow(
                UI.Label(text=h.ip),
                UI.Label(text=h.name),
                UI.Label(text=h.aliases),
                UI.DataTableCell(
                    UI.HContainer(
                        UI.MiniButton(
                            id='edit/' + str(self.hosts.index(h)), 
                            text='Edit'
                        ),
                        UI.WarningMiniButton(
                            id='del/' + str(self.hosts.index(h)),
                            text='Delete', 
                            msg='Remove %s from hosts'%h.ip
                        )
                    ),
                    hidden=True
                )
            ))
        t = UI.VContainer(t, UI.Button(text='Add host', id='add'))

        if self._editing is not None:
            try:
                h = self.hosts[self._editing]
            except:
                h = backend.Host()
            t.append(self.get_ui_edit(h))

        panel.append(t)
        return panel

    def get_ui_edit(self, h):
        dlg = UI.DialogBox(
            UI.VContainer(
                UI.LayoutTable(
                    UI.LayoutTableRow(
                        UI.Label(text='IP address:'), 
                        UI.TextInput(name='ip', value=h.ip)
                    ),
                    UI.LayoutTableRow(
                        UI.Label(text='Hostname:'), 
                        UI.TextInput(name='name', value=h.name)
                    ),
                    UI.LayoutTableRow(
                        UI.Label(text='Aliases:'), 
                        UI.TextInput(name='aliases', value=h.aliases)
                    )
            )),
            id = 'dlgEdit'
        )

        return dlg

    @event('minibutton/click')
    @event('button/click')
    @event('linklabel/click')
    def on_click(self, event, params, vars = None):
        if params[0] == 'add':
            self._editing = len(self.hosts)
        if params[0] == 'edit':
            self._editing = int(params[1])
        if params[0] == 'del':
            self.hosts.pop(int(params[1]))
            backend.save(self.hosts)

    @event('dialog/submit')
    def on_submit(self, event, params, vars = None):
        if params[0] == 'dlgEdit':
            v = vars.getvalue('value', '')
            if vars.getvalue('action', '') == 'OK':
                h = backend.Host()
                h.ip = vars.getvalue('ip', 'none')
                h.name = vars.getvalue('name', 'none')
                h.aliases = vars.getvalue('aliases', '')
                try:
                    self.hosts[self._editing] = h
                except:
                    self.hosts.append(h)
                backend.save(self.hosts)
            self._editing = None


class HostsContent(ModuleContent):
    module = 'hosts'
    path = __file__
