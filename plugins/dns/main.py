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
        ui = self.app.inflate('dns:main')
        td = ui.find('list')

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

        if self._editing_ns == None:
            ui.remove('dlgEdit')
        else:
            ns = self.config.nameservers[self._editing_ns]
            classes = ['nameserver', 'domain', 'search', 'sortlist', 'options']
            for c in classes:
                e = ui.find('cls-' + c)
                e.set('value', c)
                e.set('selected', ns.cls==c)
            ui.find('value').set('value', ns.address)    
        
        return ui


        
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
