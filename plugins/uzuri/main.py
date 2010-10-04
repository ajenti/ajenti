import time

from ajenti.ui import *
from ajenti.com import implements
from ajenti.app.api import ICategoryProvider
from ajenti.app.helpers import *
from ajenti.utils import *

from ajenti.plugins.uzuri_common import UzuriMaster, ClusterNode


class UzuriMasterPlugin(CategoryPlugin):
    text = 'Uzuri'
    icon = '/dl/uzuri/icon_small.png'
    folder = 'top'

    def on_session_start(self):
        self._tab = 0
        self._editing_node = None
        self._editing_parts = False
        self._editing_var = None
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
        vc = UI.VContainer(spacing=20)
        if self._master.is_busy():
            vc.append(UI.HContainer(
                         UI.Image(file='/dl/core/ui/ajax.gif'),
                         UI.Label(text='Deploying to ' + self._master.worker.status,
                                  size=2),
                         UI.Refresh(time=3000),
                         UI.WarningMiniButton(text='Abort', id='abort', msg='Abort deployment. This may leave current node in unconfigured state.'),
                    ))

        if self._master.is_installed():
            ui = UI.TabControl(active=self._tab)
            ui.add('Nodes', self.get_ui_nodes())
            ui.add('Variables', self.get_ui_vars())
        else:
            ui = UI.ErrorBox(
                    title='Not configured', 
                    text='You need to autoconfigure Uzuri first'
                 )
            
                 
        vc.append(ui)                 
        return vc


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
                    ),
                    UI.Button(text='Choose parts', id='parts')
                )
            )
            
        if self._editing_node is not None:
            ui.append(self.get_ui_edit_node(self._editing_node))

        if self._editing_parts:
            ui.append(self.get_ui_edit_parts())
            
        return ui
        
    def get_ui_edit_node(self, node=ClusterNode()):
        ui = UI.LayoutTable(
                UI.LayoutTableRow(
                    UI.Label(text='Address:'),
                    UI.TextInput(name='addr', value=node.address)
                ),
                UI.LayoutTableRow(
                    UI.Label(text='Port:'),
                    UI.TextInput(name='port', value=node.port)
                )
            )
            
        for k in self._master.cfg.vars:
            if k in node.vars.keys():
                v = node.vars[k]
            else:
                v = ''
                
            ui.append(
                UI.LayoutTableRow(
                    UI.Label(text='{u:%s}'%k),
                    UI.TextInput(name='var_'+k, value=v)
                ))
       
        return UI.DialogBox(ui, id='dlgEditNode')

    def get_ui_edit_parts(self, node=ClusterNode()):
        ui = UI.VContainer()
            
        for p in self._master.get_parts():
            ui.append(UI.Checkbox(
                    name='part_'+p.id,
                    text=p.name,
                    checked=p.id in self._master.cfg.parts
                ))
       
        return UI.DialogBox(ui, id='dlgEditParts')
         
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
                        UI.HContainer(
                            UI.MiniButton(
                                id='editvar/'+n,
                                text='Edit',
                            ),
                            UI.MiniButton(
                                id='deletevar/'+n,
                                text='Delete',
                            ),
                            spacing=0
                        ),
                        hidden=True
                    )
                )
            )
        
        ui = UI.VContainer(
                tbl,
                UI.Button(text='Add variable', id='addvar')
            )
            
        if self._editing_var is not None:
           ui.append(UI.InputBox(text='Name:', value=self._editing_var, id='dlgEditVar'))
        return ui
        
    @event('minibutton/click')
    @event('button/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'prepare':
            self._master.install()
        if params[0] == 'enableroot':
            self._master.enable()
        if params[0] == 'disableroot':
            self._master.disable()
        if params[0] == 'editnode':
            self._tab = 0
            
            self._editing_node = \
                filter(
                    lambda x:x.address==params[1], 
                    self._master.cfg.nodes
                )[0]
        if params[0] == 'addnode':
            self._tab = 0
            self._editing_node = ClusterNode()
        if params[0] == 'deletenode':
            self._tab = 0
            self._master.cfg.nodes = \
                filter(
                    lambda x:x.address!=params[1], 
                    self._master.cfg.nodes
                )
            self._master.cfg.save()
        if params[0] == 'deploy':
            self._tab = 0
            self._master.deploy_node(
                filter(
                    lambda x:x.address==params[1], 
                    self._master.cfg.nodes
                )[0])
        if params[0] == 'deployall':
            self._tab = 0
            self._master.deploy_all()
        if params[0] == 'parts':
            self._tab = 0
            self._editing_parts = True
        if params[0] == 'editvar':
            self._tab = 1
            self._editing_var = params[1]
        if params[0] == 'addvar':
            self._tab = 1
            self._editing_var = ''
        if params[0] == 'deletevar':
            self._tab = 1
            self._master.cfg.vars.remove(params[1])
            self._master.cfg.save()
        if params[0] == 'abort':
            self._master.worker.kill()

    @event('dialog/submit')
    def on_submit(self, event, params, vars):
        if params[0] == 'dlgEditVar':
            if vars.getvalue('action', '') == 'OK':
                v = self._editing_var
                if v in self._master.cfg.vars:
                    self._master.cfg.vars.remove(v)
                self._master.cfg.vars.append(vars.getvalue('value'))
                self._master.cfg.save()
            self._editing_var = None
        if params[0] == 'dlgEditNode':
            if vars.getvalue('action', '') == 'OK':
                n = self._editing_node
                n.address = vars.getvalue('addr', '')
                n.port = vars.getvalue('port', '22')
                for k in self._master.cfg.vars:
                    n.vars[k] = vars.getvalue('var_'+k, '')
                if not n in self._master.cfg.nodes:
                    self._master.cfg.nodes.append(n)
                self._master.cfg.save()
            self._editing_node = None
        if params[0] == 'dlgEditParts':
            if vars.getvalue('action', '') == 'OK':
                self._master.cfg.parts = []
                for p in self._master.get_parts():
                    if vars.getvalue('part_'+p.id,'') == '1':
                        self._master.cfg.parts.append(p.id)
                self._master.cfg.save()
            self._editing_parts = False
            
            
class UzuriContent(ModuleContent):
    module = 'uzuri'
    path = __file__
    widget_files = []
    css_files = []
    
