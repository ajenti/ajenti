from ajenti.ui import *
from ajenti.com import implements
from ajenti.app.api import ICategoryProvider
from ajenti.app.helpers import *
import backend

class CronPlugin(CategoryPlugin):
    implements((ICategoryProvider, 90))

    text = 'Cron'
    description = 'Cron plugin'
    icon = '/dl/cron/icon.png'

    def on_session_start(self):
        self._labeltext = ''
        self._editing = -1
        self._tasks = []
        self._others = []

    def get_ui(self):
        panel = UI.PluginPanel(UI.Label(text=self._log),
                               title='Crontab',
                               icon='/dl/filesystems/icon.png')
        panel.appendChild(self.get_default_ui())
        return panel
        
    def get_default_ui(self):
        table = UI.DataTable(UI.DataTableRow(
                UI.Label(text='Minutes'),
                UI.Label(text='Hours'),
                UI.Label(text='Days'),
                UI.Label(text='Months'),
                UI.Label(text='DoW'),
                UI.Label(text='Command'),
                UI.Label(text=''),
                header=True,
               ))
        self._tasks, self._others = backend.read_crontab()
        for i, t in enumerate(self._tasks):
            table.appendChild(UI.DataTableRow(
                    UI.Label(text=t.m),
                    UI.Label(text=t.h),
                    UI.Label(text=t.dom),
                    UI.Label(text=t.mon),
                    UI.Label(text=t.dow),
                    UI.Label(text=t.command),
                    UI.DataTableCell(
                        UI.HContainer(
                            UI.MiniButton(id='edit/' + str(i),
                                text='Edit'),
                            UI.WarningMiniButton(id='del/' + str(i),
                                text='Delete')
                        ),
                        hidden=True)
                    ))
        vbox = UI.VContainer(table, UI.Button(text='Add task', id='add'))
        if self._editing != -1:
            try:
                task = self._tasks[self._editing]
            except IndexError:
                task = backend.Task()
            vbox.vnode(self.get_ui_edit(task))
        
        return vbox
    
    def get_ui_edit(self, e):
        pass
    
    @event('minibutton/click')
    @event('button/click')
    @event('linklabel/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'add':
            self._editing = len(self._tasks)
        if params[0] == 'edit':
            print params
            #self._editing = int(params[1])
        if params[0] == 'del':
            self._tasks.pop(int(params[1]))
            backend.write_crontab(self._others + self._tasks)
    #@event('action/click')
    #def on_click(self, event, params, vars=None):
        #if params[0] == 'act-go':
            #self._labeltext += 'Kaboom! '

class CronContent(ModuleContent):
    module = 'cron'
    path = __file__
