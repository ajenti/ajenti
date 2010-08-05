from ajenti.ui import *
from ajenti.app.helpers import CategoryPlugin, ModuleContent, event
from api import *

class NetworkContent(ModuleContent):
    module = 'network'
    path = __file__

class NetworkPlugin(CategoryPlugin):
    text = 'Network'
    icon = '/dl/network/icon.png'
    folder = 'system'

    def on_init(self):
        self.net_config = self.app.grab_plugins(INetworkConfig)[0]

    def on_session_start(self):
        self._editing_iface = ""
        self._editing_ns = -1

    def get_ui(self):
        panel = UI.PluginPanel(UI.Label(text=""), title='Networking', icon='/dl/network/icon.png')
        
        ui = UI.VContainer(
                self.get_ui_ifaces(),
                UI.Spacer(height=20),
                self.get_ui_dns()
             )
        panel.appendChild(ui)
        return panel

    def get_ui_ifaces(self):
        ti = UI.DataTable()
        hr = UI.DataTableRow(
                UI.DataTableCell(UI.Label(text='Interface'), width="100px"),
                UI.DataTableCell(UI.Label(text='Class'), width="100px"),
                UI.DataTableCell(UI.Label(text='Address'), width="100px"),
                UI.DataTableCell(UI.Label(text='Status'), width="100px"),
                UI.DataTableCell(UI.Label(text='')),
                header=True
             )
        ti.appendChild(hr)

        for x in self.net_config.interfaces:
            i = self.net_config.interfaces[x]
            ti.appendChild(UI.DataTableRow(
                            UI.Label(text=i.name),
                            UI.Label(text=i.clsname),
                            UI.Label(text=i.addr),
                            UI.HContainer(
                                UI.Image(file='/dl/network/%s.png'%('up' if i.up else 'down')),
                                UI.Label(text=('Up' if i.up else 'Down')),
                            ),
                            UI.DataTableCell(
                                UI.HContainer(
                                    UI.MiniButton(text='Edit', id='editiface/' + i.name),
                                    UI.WarningMiniButton(text=('Down' if i.up else 'Up'), id=('if' + ('down' if i.up else 'up') + '/' + i.name))
                                ),
                                hidden=True
                            )
                           ))

        c = UI.VContainer(
                UI.Label(text='Network interfaces', size=3),
                UI.Spacer(height=10),
                ti,
            )               

        if self._editing_iface != "":
            cnt = UI.TabControl()
            for x in self.net_config.interfaces[self._editing_iface].bits:
                cnt.add(x.title, x.get_ui())
            dlg = UI.DialogBox(
                        cnt,
                        title="Interface '" + self._editing_iface + "' properties",
                        id="dlgEditIface"
                    )
            c.vnode(dlg)

        return c
    
    def get_ui_dns(self):
        td = UI.DataTable()
        hr = UI.DataTableRow(
                UI.DataTableCell(UI.Label(text='Type'), width="100px"),
                UI.DataTableCell(UI.Label(text='Address'), width="200px"),
                UI.DataTableCell(UI.Label(text='')),
                header=True
             )
        td.appendChild(hr)

        for x in range(0, len(self.net_config.nameservers)):
            i = self.net_config.nameservers[x]
            td.appendChild(UI.DataTableRow(
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
                UI.Label(text='DNS options', size=3),
                UI.Spacer(height=10),
                td,
                UI.Spacer(height=10),
                UI.Button(text='Add option', id='addns')
            )               

        if self._editing_ns != -1:
            dlg = UI.DialogBox(
                        self.net_config.ns_edit_dialog(self.net_config.nameservers[self._editing_ns]),
                        title="Nameserver entry options", id="dlgEditNS"
                    )
            c.vnode(dlg)       

        return c
        
    @event('button/click')
    @event('minibutton/click')
    @event('linklabel/click')
    def on_ll_click(self, event, params, vars=None):
        if params[0] == 'editiface':
            self._editing_iface = params[1]
        if params[0] == 'editns':
            self._editing_ns = int(params[1])
        if params[0] == 'delns':
            self.net_config.nameservers.remove(self.net_config.nameservers[int(params[1])])
            self.net_config.save()
        if params[0] == 'ifup':
            self.net_config.up(self.net_config.interfaces[params[1]])
        if params[0] == 'ifdown':
            self.net_config.down(self.net_config.interfaces[params[1]])
        if params[0] == 'addns':
            self.net_config.nameservers.append(self.net_config.new_nameserver())
            self._editing_ns = len(self.net_config.nameservers) - 1

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

