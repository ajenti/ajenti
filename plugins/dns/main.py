from ajenti.ui import *
from ajenti.api import *

from api import *


class DNSPlugin(CategoryPlugin):
    text = 'DNS '
    icon = '/dl/dns/icon.png'
    folder = 'system'

    def on_init(self):
        self.config = self.app.get_backend(IDNSConfig)

    def on_session_start(self):
        self._editing_ns = None

    def get_ui(self):
        l = len(self.config.nameservers)
        panel = UI.PluginPanel(
                    UI.Label(text='%i entries'%l), 
                    title='DNS Nameservers', 
                    icon='/dl/dns/icon.png'
                )
        panel.append(self.get_main_ui())
        return panel
        
    def get_main_ui(self):
        td = UI.DataTable()
        hr = UI.DataTableRow(
                UI.DataTableCell(UI.Label(text='Type'), width="100px"),
                UI.DataTableCell(UI.Label(text='Address'), width="200px"),
                UI.DataTableCell(UI.Label(text='')),
                header=True
             )
        td.append(hr)

        for x in range(0, len(self.config.nameservers)):
            i = self.config.nameservers[x]
            td.append(UI.DataTableRow(
                            UI.Label(text=i.cls),
                            UI.Label(text=i.address),
                            UI.DataTableCell(
                                UI.HContainer(
                                    UI.MiniButton(text='Edit', id='editns/' + str(x)),
                                    UI.MiniButton(text='Remove', id='delns/' + str(x))
                                ),
                                hidden=True
                            )
                           ))

        c = UI.VContainer(
                td,
                UI.Button(text='Add option', id='addns'),
            )

        if self._editing_ns != None:
            c.append(self.get_ui_edit(self.config.nameservers[self._editing_ns]))

        return c


    def get_ui_edit(self, ns):
        p = UI.LayoutTable(
                UI.LayoutTableRow(
                    UI.Label(text='Type:'),
                    UI.Select(
                        UI.SelectOption(text='Nameserver', value='nameserver', selected=(ns.cls=='nameserver')),
                        UI.SelectOption(text='Local domain', value='domain', selected=(ns.cls=='domain')),
                        UI.SelectOption(text='Search list', value='search', selected=(ns.cls=='search')),
                        UI.SelectOption(text='Sort list', value='sortlist', selected=(ns.cls=='sortlist')),
                        UI.SelectOption(text='Options', value='options', selected=(ns.cls=='options')),
                        name='cls'
                    ),
                UI.LayoutTableRow(
                    UI.Label(text='Value:'),
                    UI.TextInput(name='address', value=ns.address),
                    )
                )
            )
        return UI.DialogBox(p, id='dlgEdit')
        
    @event('button/click')
    @event('minibutton/click')
    def on_ll_click(self, event, params, vars=None):
        if params[0] == 'editns':
            self._editing_ns = int(params[1])
        if params[0] == 'delns':
            self.config.nameservers.pop(int(params[1]))
            self.config.save()
        if params[0] == 'addns':
            self.config.nameservers.append(Nameserver())
            self._editing_ns = len(self.config.nameservers) - 1

    @event('dialog/submit')
    def on_dlg_submit(self, event, params, vars=None):
        if params[0] == 'dlgEdit':
            if vars.getvalue('action', '') == 'OK':
                try:
                    i = self.config.nameservers[self._editing_ns]
                except:
                    i = Nameserver()
                    self.config.nameservers.append(i)

                i.cls = vars.getvalue('cls', 'nameserver')
                i.address = vars.getvalue('address', '127.0.0.1')
                self.config.save()
            self._editing_ns = None
