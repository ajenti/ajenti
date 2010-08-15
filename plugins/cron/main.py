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
        self._newtask = False

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
        if self._newtask or t.special:
            tabbar.add("Special", self.get_ui_special(t))
        if self._newtask or not t.special:
            tabbar.add("Advanced", self.get_ui_advanced(t))
        if self._newtask:
            tabbar.add("Template", self.get_ui_template())
        
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
    
    def get_ui_template(self):
        tabbar = UI.TabControl(active=self._tab)
        tabbar.add("Every Minutes", self.get_ui_temp_minutes())
        tabbar.add("Every hours", self.get_ui_temp_hours())
        tabbar.add("Every days", self.get_ui_temp_days())
        tabbar.add("Every months", self.get_ui_temp_days())
        return tabbar
    
    def get_ui_temp_minutes(self):
        temp_table = UI.LayoutTable(
                    UI.LayoutTableRow(
                        UI.LayoutTableCell(
                            UI.Label(text='Start task every'),
                            width = '60%'
                            ),
                        UI.LayoutTableCell(
                            UI.TextInput(name='minutes'),
                            width = '20%'
                            ),
                        UI.LayoutTableCell(
                            UI.Label(text='minutes'),
                            width = '20%'
                            )
                        ),
                    UI.LayoutTableRow(
                        UI.LayoutTableCell(
                            UI.Label(text='Command'),
                            colspan=1
                        ),
                        UI.LayoutTableCell(
                            UI.TextInput(name='command'),
                            colspan=2
                            )
                    ))
        return UI.FormBox(temp_table, id='frmTempMinutes')
    
    def get_ui_temp_hours(self):
        temp_table = UI.LayoutTable(
                    UI.LayoutTableRow(
                        UI.LayoutTableCell(
                            UI.Label(text='Start task every'),
                            width = '60%'
                            ),
                        UI.LayoutTableCell(
                            UI.TextInput(name='hours'),
                            width = '20%'
                            ),
                        UI.LayoutTableCell(
                            UI.Label(text='hours'),
                            width = '20%'
                            )
                        ),
                    UI.LayoutTableRow(
                        UI.LayoutTableCell(
                            UI.Label(text='Command'),
                        ),
                        UI.LayoutTableCell(
                            UI.TextInput(name='command'),
                            colspan=2
                            )
                    ))
        return UI.FormBox(temp_table, id='frmTempHours')

    def get_ui_temp_days(self):
        hour_select = [UI.SelectOption(text=str(h), value=str(h))
                        for h in range(24)]
        minute_select = [UI.SelectOption(text=str(m), value=str(m))
                        for m in range(60)]
        temp_table = UI.VContainer(
                    UI.Hcontainer(
                        UI.Hnode(
                            UI.Label(text='Start task every'),
                            width = '60%'
                            ),
                        UI.Hnode(
                            UI.TextInput(name='days'),
                            width = '20%'
                            ),
                        UI.Hnode(
                            UI.Label(text='days'),
                            width = '20%'
                            )
                        ),
                    UI.Hcontainer(
                        UI.Hnode(
                            UI.Label(text='At'),
                        ),
                        UI.Hnode(
                            UI.Select(*hour_select,
                            name='hour'),
                        ),
                        UI.Hnode(
                            UI.Label(text='hour'),
                        ),
                        UI.Hnode(
                            UI.Select(*minute_select,
                            name='minute'),
                        ),
                        UI.Hnode(
                            UI.Label(text='minute'),
                        ),
                    ),
                    UI.Hcontainer(
                        UI.Hnode(
                            UI.Label(text='Command'),
                        ),
                        UI.Hnode(
                            UI.TextInput(name='command'),
                            colspan=2
                            )
                    ))
        return UI.FormBox(temp_table, id='frmTempDays')
    
    def get_ui_temp_months(self):
        hour_select = [UI.SelectOption(text=str(h), value=str(h))
                        for h in range(24)]
        minute_select = [UI.SelectOption(text=str(m), value=str(m))
                        for m in range(60)]
        day_select = [UI.SelectOption(text=str(d), value=str(d))
                        for m in range(1, 32)]
        temp_table = UI.VContainer(
                    UI.Hcontainer(
                        UI.Hnode(
                            UI.Label(text='Start task every'),
                            width = '60%'
                            ),
                        UI.Hnode(
                            UI.TextInput(name='months'),
                            width = '20%'
                            ),
                        UI.Hnode(
                            UI.Label(text='months'),
                            width = '20%'
                            )
                        ),
                    UI.Hcontainer(
                        UI.Hnode(
                            UI.Label(text='At'),
                        ),
                        UI.Hnode(
                            UI.Select(*day_select,
                            name='day'),
                        ),
                        UI.Hnode(
                            UI.Label(text='day'),
                        ),
                        UI.Hnode(
                            UI.Select(*hour_select,
                            name='hour'),
                        ),
                        UI.Hnode(
                            UI.Label(text='hour'),
                        ),
                        UI.Hnode(
                            UI.Select(*minute_select,
                            name='minute'),
                        ),
                        UI.Hnode(
                            UI.Label(text='minute'),
                        ),
                    ),
                    UI.Hcontainer(
                        UI.Hnode(
                            UI.Label(text='Command'),
                        ),
                        UI.Hnode(
                            UI.TextInput(name='command'),
                            colspan=2
                            )
                    ))
        return UI.FormBox(temp_table, id='frmTempMonths')

    @event('minibutton/click')
    @event('button/click')
    @event('linklabel/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'add':
            self._editing = len(self._tasks)
            self._show_dialog = 1
            self._newtask = True
        if params[0] == 'edit':
            self._editing = int(params[1])
            self._show_dialog = 1
        if params[0] == 'del':
            self._tasks.pop(int(params[1]))
            self._error = backend.write_crontab(self._others +\
                                                self._tasks)
        
    @event('form/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'frmAdvanced' and\
                vars.getvalue('action') == 'OK':
            task_str = ' '.join((
                        vars.getvalue('m').replace(' ', '') or '*',
                        vars.getvalue('h').replace(' ', '') or '*',
                        vars.getvalue('dom').replace(' ', '') or '*',
                        vars.getvalue('mon').replace(' ', '') or '*',
                        vars.getvalue('dow').replace(' ', '') or '*'
                        ))
            task_str += '\t' + vars.getvalue('command')
            if self.set_task(task_str):
                return 1
        elif params[0] == 'frmSpecial' and\
                vars.getvalue('action') == 'OK':
            task_str = '@' + vars.getvalue('special')
            task_str += '\t' + vars.getvalue('command')
            if self.set_task(task_str):
                return 1
        elif params[0] == 'frmTempMinutes' and\
                vars.getvalue('action') == 'OK':
            task_str = '*/' + (vars.getvalue('minutes') or '1')
            task_str += ' * * * *'
            task_str += '\t' + vars.getvalue('command')
            print task_str
            if self.set_task(task_str):
                return 1
        elif params[0] == 'frmTempHours' and\
                vars.getvalue('action') == 'OK':
            task_str = '0 ' + '*/' + (vars.getvalue('hours')  or '1')
            task_str += ' * * *'
            task_str += '\t' + vars.getvalue('command')
            print task_str
            if self.set_task(task_str):
                return 1
        elif params[0] == 'frmTempDays' and\
                vars.getvalue('action') == 'OK':
            task_str = vars.getvalue('minute') + ' '
            task_str += vars.getvalue('hour') + ' '
            task_str += '*/' + (vars.getvalue('days')  or '1')
            task_str += ' * *'
            task_str += '\t' + vars.getvalue('command')
            print task_str
            if self.set_task(task_str):
                return 1
        elif params[0] == 'frmTempMonths' and\
                vars.getvalue('action') == 'OK':
            task_str = vars.getvalue('minute') + ' '
            task_str += vars.getvalue('hour') + ' '
            task_str += vars.getvalue('day') + ' '
            task_str += '*/' + (vars.getvalue('months')  or '1')
            task_str += ' *'
            task_str += '\t' + vars.getvalue('command')
            print task_str
            if self.set_task(task_str):
                return 1
        self._show_dialog = 0
        self._editing = -1
        self._newtask = False
    
    def set_task(self, task_str):
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
        return 0

class CronContent(ModuleContent):
    module = 'cron'
    path = __file__
    
