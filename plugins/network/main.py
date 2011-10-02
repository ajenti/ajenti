from ajenti.ui import *
from ajenti.api import CategoryPlugin, event

from api import *


class NetworkPlugin(CategoryPlugin):
    text = 'Network'
    icon = '/dl/network/icon.png'
    folder = 'hardware'

    def on_init(self):
        self.net_config = self.app.get_backend(INetworkConfig)

    def on_session_start(self):
        self._editing_iface = ""
        self._info = None
        
    def get_ui(self):
        ui = self.app.inflate('network:main')
        ti = ui.find('list')
        
        for x in self.net_config.interfaces:
            i = self.net_config.interfaces[x]
            ti.append(UI.DTR(
                            UI.Label(text=i.name),
                            UI.Label(text=i.devclass),
                            UI.Label(text=self.net_config.get_ip(i)),
                            UI.HContainer(
                                UI.Image(file='/dl/network/%s.png'%('up' if i.up else 'down')),
                                UI.Label(text=('Up' if i.up else 'Down')),
                            ),
                            UI.HContainer(
                                UI.TipIcon(icon='/dl/core/ui/stock/info.png',
                                    text='Info', id='info/' + i.name),
                                UI.TipIcon(icon='/dl/core/ui/stock/edit.png',
                                    text='Edit', id='editiface/' + i.name),
                                UI.TipIcon(icon='/dl/core/ui/stock/service-%s.png'%('run' if not i.up else 'stop'), 
                                    text=('Down' if i.up else 'Up'), 
                                    id=('if' + ('down' if i.up else 'up') + '/' + i.name), 
                                    warning='Bring %s interface %s' % (('Down' if i.up else 'Up'), i.name)
                                )
                            ),
                           ))

        c = ui.find('main')

        if self._info is not None:
            c.append(
                UI.DialogBox(
                    self.net_config.get_info(self.net_config.interfaces[self._info]),
                    id='dlgInfo', 
                    hidecancel=True
                ))
        
        if self._editing_iface != "":
            cnt = UI.TabControl(active=0)
            for x in self.net_config.interfaces[self._editing_iface].bits:
                cnt.add(x.title, x.get_ui())
            dlg = UI.DialogBox(
                        cnt,
                        id="dlgEditIface"
                    )
            c.append(dlg)

        return ui

    @event('button/click')
    @event('linklabel/click')
    def on_ll_click(self, event, params, vars=None):
        if params[0] == 'info':
            self._info = params[1]
        if params[0] == 'editiface':
            self._editing_iface = params[1]
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
        if params[0] == 'dlgInfo':
            self._info = None

