import time

from ajenti.ui import *
from ajenti.com import implements
from ajenti.app.api import ICategoryProvider
from ajenti.app.helpers import *
from ajenti.utils import *

from ajenti.plugins.uzuri_common import UzuriMaster


class UzuriMasterPlugin(CategoryPlugin):
    text = 'Uzuri'
    icon = '/dl/uzuri/icon_small.png'
    folder = 'top'

    def on_session_start(self):
        self._tab = 0
        self._master = UzuriMaster(self.app)
        self._master.load()
                
    def get_ui(self):
        if self._master.is_installed():
            if self._master.is_enabled():
                ctl = UI.WarningButton(
                            text='Configure local machine',
                            id='disableroot',
                            msg='Switch Ajenti to configure current host'
                        )
            else:
                ctl = UI.WarningButton(
                            text='Configure cluster',
                            id='enableroot',
                            msg='Switch Ajenti to configure the cluster'
                        )
        else:
            ctl = UI.WarningButton(
                        text='Autoconfigure',
                        id='prepare',
                        msg='Configure Uzuri. This may take some time.'
                    )
                
        panel = UI.PluginPanel(ctl, title='Uzuri clustering', icon='/dl/uzuri/icon.png')
        panel.append(self.get_default_ui())
        return panel

    def get_default_ui(self):
        ui = None
        
        if self._master.is_installed():
            ui = UI.TabControl(active=self._tab)
            ui.add('Nodes', self.get_ui_nodes())
            ui.add('Variables', self.get_ui_vars())
        else:
            ui = UI.ErrorBox(
                    title='Not configured', 
                    text='You need to autoconfigure Uzuri first'
                 )
            
        return ui


    def get_ui_nodes(self):
        tbl = UI.DataTable(
                UI.DataTableRow(
                    UI.Label(),
                    UI.Label(text='Address'),
                    UI.Label(text='Last deployed'),
                    UI.Label(),
                    header=True
                )
            )
        
        for n in self._master.cfg.nodes:
            t = time.localtime(int(n.timestamp))
            t = time.strftime('%a, %d %b %Y %H:%M:%S', t)
            if n.timestamp == '0':
                t = 'Never'
            tbl.append(
                UI.DataTableRow(
                    UI.Image(file='/dl/uzuri/node.png'),
                    UI.Label(text=n.address+':'+n.port),
                    UI.Label(text=t),
                    UI.DataTableCell(
                        UI.HContainer(
                            UI.WarningMiniButton(
                                id='deploy/'+n.address,
                                text='Deploy',
                                msg='Deploy configuration to node '+n.address
                            ),
                            UI.MiniButton(id='editnode/'+n.address, text='Edit'),
                            UI.WarningMiniButton(
                                id='deletenode/'+n.address,
                                text='Delete',
                                msg='Delete node '+n.address
                            ),
                            spacing=0
                        ),
                        hidden=True
                    )
                )
            )
        
        ui = UI.VContainer(
                tbl,
                UI.HContainer(
                    UI.Button(text='Add node', id='addnode'),
                    UI.WarningButton(
                        text='Deploy all', 
                        id='deployall',
                        msg='Deploy configuration to all nodes'
                    )
                )
            )
            
        return ui
        
    def get_ui_vars(self):
        tbl = UI.DataTable(
                UI.DataTableRow(
                    UI.Label(text='Name'),
                    UI.Label(),
                    header=True
                )
            )
        
        for n in self._master.cfg.vars:
            tbl.append(
                UI.DataTableRow(
                    UI.Label(text=n),
                    UI.DataTableCell(
                        UI.MiniButton(
                            id='deletevar/'+n,
                            text='Delete',
                        ),
                        hidden=True
                    )
                )
            )
        
        ui = UI.VContainer(
                tbl,
                UI.Button(text='Add variable', id='addvar')
            )
            
        return ui
        
    @event('minibutton/click')
    @event('button/click')
    @event('linklabel/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'prepare':
            self._master.install()
        if params[0] == 'enableroot':
            self._master.enable()
        if params[0] == 'disableroot':
            self._master.disable()

            
class UzuriContent(ModuleContent):
    module = 'uzuri'
    path = __file__
    widget_files = []
    css_files = []
    
