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
        self._editing_iface = ""
        self._editing_ns = -1

    def get_ui(self):
        ti = UI.DataTable()
        hr = UI.DataTableRow(
                UI.DataTableCell(UI.Label(text='Interface'), width="100px"),
                UI.DataTableCell(UI.Label(text='Class'), width="100px"),
                UI.DataTableCell(UI.Label(text='Address'), width="100px"),
                UI.DataTableCell(UI.Label(text='Status'), width="100px"),
                UI.DataTableCell(UI.Label(text='Controls'), width="100px"),
                header=True
             )
        ti.appendChild(hr)

        cup = 0
        for x in self.net_config.interfaces:
            i = self.net_config.interfaces[x]
            if i.up: cup += 1
            ti.appendChild(UI.DataTableRow(
                            UI.Label(text=i.name),
                            UI.Label(text=i.clsname),
                            UI.Label(text=i.addr),
                            UI.Label(text=('Up' if i.up else 'Down')),
                            UI.HContainer(
                                UI.LinkLabel(text='Edit', id='editiface/' + i.name),
                                UI.LinkLabel(text=('Down' if i.up else 'Up'), id=('if' + ('down' if i.up else 'up') + '/' + i.name))
                            )
                           ))

        h = UI.HContainer(
                UI.Image(file='/dl/network/bigicon.png'),
                UI.Spacer(width=10),
                UI.VContainer(
                    UI.Label(text='Network', size=5),
                    UI.Label(text='%i interfaces up out of %i total' % (cup, len(self.net_config.interfaces)))
                )
            )


        td = UI.DataTable()
        hr = UI.DataTableRow(
                UI.DataTableCell(UI.Label(text='Type'), width="100px"),
                UI.DataTableCell(UI.Label(text='Address'), width="200px"),
                UI.DataTableCell(UI.Label(text='Controls'), width="100px"),
                header=True
             )
        td.appendChild(hr)

        for x in range(0, len(self.net_config.nameservers)):
            i = self.net_config.nameservers[x]
            td.appendChild(UI.DataTableRow(
                            UI.Label(text=i.cls),
                            UI.Label(text=i.address),
                            UI.HContainer(
                                UI.LinkLabel(text='Edit', id='editns/' + str(x)),
                                UI.LinkLabel(text='Remove', id='delns/' + str(x))
                            )
                           ))

        p = UI.VContainer(
                h,
                UI.Spacer(height=20),
                UI.Label(text='Network interfaces', size=3),
                UI.Spacer(height=10),
                ti,
                UI.Spacer(height=20),
                UI.Label(text='Nameservers', size=3),
                UI.Spacer(height=10),
                td,
                UI.Spacer(height=10),
                UI.LinkLabel(text='Add new entry', id='addns')
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

        if self._editing_ns != -1:
            dlg = UI.DialogBox(
                        self.net_config.ns_edit_dialog(self.net_config.nameservers[self._editing_ns]),
                        title="Nameserver entry options", id="dlgEditNS", action="/handle/dialog/submit/dlgEditNS"
                    )
            p.vnode(dlg)

        return p

    @event('linklabel/click')
    def on_ll_click(self, event, params, vars=None):
        if params[0] == 'editiface':
            self._editing_iface = params[1]
        if params[0] == 'editns':
            self._editing_ns = int(params[1])
        if params[0] == 'delns':
            self.net_config.nameservers.remove(self.net_config.nameservers[int(params[1])])
            self.net_config.save()
        if params[0] == 'addns':
            self.net_config.nameservers.append(self.net_config.get_nameserver())
            self._editing_ns = len(self.net_config.nameservers) - 1
        if params[0] == 'ifup':
            self.net_config.up(self.net_config.interfaces[params[1]])
        if params[0] == 'ifdown':
            self.net_config.down(self.net_config.interfaces[params[1]])

    @event('dialog/submit')
    def on_dlg_submit(self, event, params, vars=None):
        if params[0] == 'dlgEditIface':
            if vars.getvalue('action', '') == 'OK':
                i = self.net_config.interfaces[self._editing_iface]
                for x in i.bits:
                    x.apply(vars)
                self.net_config.save()

            self._editing_iface = ''

        if params[0] == 'dlgEditNS':
            if vars.getvalue('action', '') == 'OK':
                try:
                    i = self.net_config.nameservers[self._editing_ns]
                except:
                    i = Nameserver()
                    self.net_config.nameservers.append(i)

                i.cls = vars.getvalue('cls', 'nameserver')
                i.address = vars.getvalue('address', '127.0.0.1')
                self.net_config.save()

            self._editing_ns = -1

