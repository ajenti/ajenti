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

    def on_init(self):
        self._tasks, self._others = backend.read_crontab()
        
    def on_session_start(self):
        self._log = ''
        self._labeltext = ''
        self._editing = -1
        self._error = ''
        self._tasks = []
        self._others = []

    def get_ui(self):
        panel = UI.PluginPanel(UI.Label(text='%s tasks' % len(self._tasks)),
                               title='Crontab',
                               icon='/dl/cron/icon.png')
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
        part = self._error.partition(":")[2]
        self._error = 'Error:' + part if part else self._error
        vbox = UI.VContainer(UI.Label(text=self._error, bold=True),
                            table,
                            UI.Button(text='Add task', id='add'),
                            )
        if self._editing != -1:
            try:
                task = self._tasks[self._editing]
            except IndexError:
                task = backend.Task()
            vbox.vnode(self.get_ui_edit(task))
        return vbox
    
    def get_ui_edit(self, t):
        vbox = UI.VContainer(UI.LayoutTable(
                    UI.LayoutTableRow(
                        UI.Label(text='Minutes'),
                        UI.TextInput(name='m', value=t.m)
                    ),
                    UI.LayoutTableRow(
                        UI.Label(text='Hours'),
                        UI.TextInput(name='h', value=t.h)
                    ),
                    UI.LayoutTableRow(
                        UI.Label(text='Days of month'),
                        UI.TextInput(name='dom', value=t.dom)
                    ),
                    UI.LayoutTableRow(
                        UI.Label(text='Months'),
                        UI.TextInput(name='mon', value=t.mon)
                    ),
                    UI.LayoutTableRow(
                        UI.Label(text='Days of week'),
                        UI.TextInput(name='dow', value=t.dow)
                    ),
                    UI.LayoutTableRow(
                        UI.Label(text='Command'),
                        UI.TextInput(name='command', value=t.command)
                    )))
        
        dlg = UI.DialogBox(
                vbox,
                title='Edit task',
                id='dlgEdit'
              )
        return dlg
    
    @event('minibutton/click')
    @event('button/click')
    @event('linklabel/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'add':
            self._editing = len(self._tasks)
        if params[0] == 'edit':
            self._editing = int(params[1])
        if params[0] == 'del':
            self._tasks.pop(int(params[1]))
            self._error = backend.write_crontab(self._others +\
                                                self._tasks)
            
    
    @event('dialog/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgEdit':
            if vars.getvalue('action', '') == 'OK':
                task_str = ' '.join((vars.getvalue('m'),
                                     vars.getvalue('h'),
                                     vars.getvalue('dom'),
                                     vars.getvalue('mon'),
                                     vars.getvalue('dow')))
                task_str += '\t' + vars.getvalue('command')
                try:
                    new_task = backend.Task(task_str)
                except:
                    self._error = "Error: Missing options."
                    self._editing = -1
                    return 1
                if self._editing < len(self._tasks):
                    self._tasks[self._editing] = new_task
                else:
                    self._tasks.append(new_task)
                self._error = backend.write_crontab(self._others +\
                                                self._tasks)
            self._editing = -1
            
class CronContent(ModuleContent):
    module = 'cron'
    path = __file__
    
