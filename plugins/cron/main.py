from ajenti.ui import *
from ajenti.com import implements
from ajenti.app.api import ICategoryProvider
from ajenti.app.helpers import *

import backend


class CronPlugin(CategoryPlugin):
    implements (ICategoryProvider)

    text = 'Cron'
    description = 'Cron plugin'
    icon = '/dl/cron/icon_small.png'
    folder = 'system'

    def on_init(self):
        self._tasks, self._others = backend.read_crontab()
        
    def on_session_start(self):
        self._log = ''
        self._labeltext = ''
        self._editing = -1
        self._error = ''
        self._tasks = []
        self._others = []
        self._tab = 0
        self._show_dialog = 0

    def get_ui(self):
        panel = UI.PluginPanel(UI.Label(text='%s tasks' %
                                        len(self._tasks)),
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
            if t.special:
                table.appendChild(UI.DataTableRow(
                    UI.Label(text=t.special),
                    UI.Label(), UI.Label(), UI.Label(), UI.Label(),
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
            else:
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
        if self._error:
            er = UI.ErrorBox(title='Error', text=self._error)
        else:
            er = UI.Spacer()
        vbox = UI.VContainer(er,
                            table,
                            UI.Button(text='Add task', id='add'),
                            )
        if self._editing != -1:
            try:
                task = self._tasks[self._editing]
            except IndexError:
                task = backend.Task()
            if self._show_dialog:
                vbox.vnode(self.get_ui_edit(task))
        return vbox
    
    def get_ui_edit(self, t):
        tabbar = UI.TabControl(active=self._tab)
        tabbar.add("Advanced", self.get_ui_advanced(t))
        tabbar.add("Special", self.get_ui_special(t))
        dlg = UI.DialogBox(
                tabbar,
                title='Edit task',
                id='dlgEdit',
                hideok=True,
                hidecancel=True
              )
        return dlg
    
    def get_ui_advanced(self, t):
        adv_table = UI.LayoutTable(
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
                    ))
        return UI.FormBox(adv_table, id='frmAdvanced')
    
    def get_ui_special(self, t):
        spc_table = UI.LayoutTable(
                    UI.LayoutTableRow(
                        UI.Radio(value="reboot", text="reboot",
                                name="special", checked=True),
                        UI.Radio(value="hourly", text="hourly",
                                name="special")),
                    UI.LayoutTableRow(
                        UI.Radio(value="daily", text="daily",
                                name="special"),
                        UI.Radio(value="weekly", text="weekly",
                                name="special")),
                    UI.LayoutTableRow(
                        UI.Radio(value="monthly", text="monthly",
                                name="special"),
                        UI.Radio(value="yearly", text="yearly",
                                name="special")),
                    UI.LayoutTableRow(
                            UI.Label(text='Command'),
                            UI.TextInput(name='command',
                                        value=t.command)
                    ))
        return UI.FormBox(spc_table, id='frmSpecial')
        
    @event('minibutton/click')
    @event('button/click')
    @event('linklabel/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'add':
            self._editing = len(self._tasks)
            self._show_dialog = 1
        if params[0] == 'edit':
            self._editing = int(params[1])
            self._show_dialog = 1
        if params[0] == 'del':
            self._tasks.pop(int(params[1]))
            self._error = backend.write_crontab(self._others +\
                                                self._tasks)
        if params[0] == 'cancel':
            print vars.getvalue('command')
            self._show_dialog = 0
            
    
    @event('dialog/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgEdit' and\
            vars.getvalue('action', '') == 'OK':
            print self._tab
            if self._tab == 0:
                task_str = ' '.join((
                        vars.getvalue('m').replace(' ', '') or '*',
                        vars.getvalue('h').replace(' ', '') or '*',
                        vars.getvalue('dom').replace(' ', '') or '*',
                        vars.getvalue('mon').replace(' ', '') or '*',
                        vars.getvalue('dow').replace(' ', '') or '*'
                        ))
                task_str += '\t' + vars.getvalue('command')
                try:
                    new_task = backend.Task(task_str)
                except:
                    self._error = "Error: Wrong options."
                    self._editing = -1
                    return 1
                if self._editing < len(self._tasks):
                    self._tasks[self._editing] = new_task
                else:
                    self._tasks.append(new_task)
                self._error = backend.write_crontab(self._others +\
                                                self._tasks)
                if self._error:
                    self._tasks, self._others = backend.read_crontab()
            elif self._tab == 1:
                task_str = '@' + vars.getvalue('special')
                print vars.getvalue('special')
                print task_str
                print vars.getvalue('command')
                print type(task_str)
                print type(vars.getvalue('command'))
                task_str += '\t' + vars.getvalue('command')
                try:
                    new_task = backend.Task(task_str)
                except:
                    self._error = "Error: Wrong options."
                    self._editing = -1
                    return 1
                if self._editing < len(self._tasks):
                    self._tasks[self._editing] = new_task
                else:
                    self._tasks.append(new_task)
                self._error = backend.write_crontab(self._others +\
                                                self._tasks)
                if self._error:
                    self._tasks, self._others = backend.read_crontab()
        self._editing = -1
        self._tab = 0
            
class CronContent(ModuleContent):
    module = 'cron'
    path = __file__
    
