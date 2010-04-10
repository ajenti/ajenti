from ajenti.ui import *
from ajenti.app.helpers import CategoryPlugin, ModuleContent, event
from api import *

class NetworkContent(ModuleContent):
    module = 'network'
    path = __file__

class NetworkPlugin(CategoryPlugin):
    text = 'Network'
    description = 'Configure adapters'
    icon = '/dl/network/icon.png'

    def on_init(self):
        self.net_config = self.app.grab_plugins(INetworkConfig)[0]

    def on_session_start(self):
        self._status_text = ''
        self._editing_iface = ""

    def get_ui(self):
        ti = UI.DataTable()
        hr = UI.DataTableRow(
                UI.DataTableCell(UI.Label(text='Interface'), width="100px"),
                UI.DataTableCell(UI.Label(text='Class'), width="100px"),
                UI.DataTableCell(UI.Label(text='Address'), width="100px"),
                UI.DataTableCell(UI.Label(text='Status'), width="100px"),
                UI.DataTableCell(UI.Label(text='Controls'), width="200px"),
                header=True
             )
        ti.appendChild(hr)

        for x in self.net_config.interfaces:
            i = self.net_config.interfaces[x]
            ti.appendChild(UI.DataTableRow(
                            UI.Label(text=i.name),
                            UI.Label(text=i.clsname),
                            UI.Label(text=i.addr),
                            UI.Label(text=('Up' if i.up else 'Down')),
                            UI.HContainer(
                                UI.LinkLabel(text='Edit', id='editiface/' + i.name)
                            )
                           ))

        h = UI.HContainer(
                UI.Image(file='/dl/network/bigicon.png'),
                UI.Spacer(width=10),
                UI.VContainer(
                    UI.Label(text='Network', size=5),
                    UI.Label(text=self._status_text)
                )
            )

        p = UI.VContainer(
                h,
                UI.Spacer(height=20),
                UI.Label(text='Network interfaces', size=3),
                UI.Spacer(height=10),
                ti
            )

        if self._editing_iface != "":
            cnt = UI.TabControl()
            for x in self.net_config.interfaces[self._editing_iface].bits:
                cnt.add(x.title, x.get_ui())
            dlg = UI.DialogBox(
                        cnt,
                        title="Interface '" + self._editing_iface + "' options", id="dlgEditIface", action="/handle/dialog/submit/dlgEditIface"
                    )
            p.vnode(dlg)

        return p

    @event('linklabel/click')
    def on_ll_click(self, event, params, vars=None):
        if params[0] == 'editiface':
            self._editing_iface = params[1]

    @event('dialog/submit')
    def on_dlg_submit(self, event, params, vars=None):
        if params[0] == 'dlgEditIface':
            if vars.getvalue('action', '') == 'OK':
                i = self.net_config.interfaces[self._editing_iface]
                for x in i.bits:
                    x.apply(vars)
                self.net_config.save()

            self._editing_iface = ''

