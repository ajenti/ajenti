from ajenti.app.api import *
from ajenti import version
from ajenti.com import *
from ajenti.ui import *
from ajenti.utils import detect_distro
from ajenti.app.helpers import *

from api import IRecoveryProvider, Manager


class RecoveryPlugin(CategoryPlugin):
    text = 'Recovery'
    icon = '/dl/recovery/icon_small.png'
    folder = 'bottom'

    def on_init(self):
        self.manager = Manager(self.app)
        self.providers = self.app.grab_plugins(IRecoveryProvider)
        self.providers = sorted(self.providers, key=lambda x: x.name)
        if not self._current:
            self._current = self.providers[0].id
            self._current_name = self.providers[0].name
        
    def on_session_start(self):
        self._err = None
        
    def get_ui(self):
        u = UI.PluginPanel(
                UI.Label(text='%i providers available' % len(self.providers)),
                self.get_default_ui(), 
                title='Configuration recovery', 
                icon='/dl/recovery/icon.png'
            )
        return u


    def get_default_ui(self):
        provs = UI.List(width=200, height=400)
                
        for p in self.providers:
            provs.append(
                    UI.ListItem(
                        UI.Label(text=p.name), 
                        id=p.id,
                        active=p.id==self._current
                    )
                  )
            
        backs = UI.DataTable(
                    UI.DataTableRow(
                        UI.Label(text='Revision'),
                        UI.Label(text='Date'),
                        UI.Label(),
                        header=True
                    ),
                    width='100%',
                    noborder=True
                )
                
        for rev in self.manager.list_backups(self._current):
            backs.append(
                UI.DataTableRow(
                    UI.Label(text=rev.revision),
                    UI.Label(text=rev.date),
                    UI.DataTableCell(
                        UI.HContainer(
                            UI.WarningMiniButton(
                                text='Recover',
                                id='restore/%s/%s'%(self._current,rev.revision),
                                msg='Restore configuration of %s as of %s (rev %s)'%(
                                        self._current_name,
                                        rev.date,
                                        rev.revision
                                    )
                            ),
                            UI.WarningMiniButton(
                                text='Drop',
                                id='drop/%s/%s'%(self._current,rev.revision),
                                msg='Delete backed up configuration of %s as of %s (rev %s)'%(
                                        self._current_name,
                                        rev.date,
                                        rev.revision
                                    )
                            ),
                            spacing=0
                        ),
                        width=0,
                        hidden=True
                    )
                )
            )       
                
        ui = UI.LayoutTable(
                   UI.LayoutTableRow(
                       UI.Label(text='Recovery providers'),
                       UI.Label(text='Backups for %s' % self._current_name),
                       UI.LayoutTableCell(
                           UI.WarningMiniButton(
                               id='backup/%s'%self._current,
                               text='Backup now',
                               msg='Backup configuration of %s'%self._current_name
                           ),
                           width=100
                       )
                   ),                    
                   UI.LayoutTableRow(
                       provs, 
                       UI.LayoutTableCell(
                           UI.ScrollContainer(
                               backs,
                               width=400,
                               height=400
                           ),
                           colspan=2
                       )
                   )
               )
               
        if self._err is not None:
            ui = UI.VContainer(UI.ErrorBox(title=self._err), ui)
            self._err = None
        return ui
                
    @event('button/click')
    @event('minibutton/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'backup':
            try:
                self.manager.backup_now(self.manager.find_provider(params[1]))
            except:
                self._err = 'Backup failed'
        if params[0] == 'restore':
            try:
                self.manager.restore_now(self.manager.find_provider(params[1]), params[2])
            except:
                self._err = 'Recovery failed'
        if params[0] == 'drop':
            try:
                self.manager.delete_backup(params[1], params[2])
            except:
                self._err = 'Deletion failed'
                        
    @event('listitem/click')
    def on_list_click(self, event, params, vars=None):
        for p in self.providers:
            if p.id == params[0]:
                self._current = p.id
                self._current_name = p.name
                

class RecoveryContent(ModuleContent):
    path = __file__
    module = 'recovery'
