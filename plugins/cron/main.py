from ajenti.ui import UI
from ajenti.api import event, helpers
from ajenti.utils import shell

import backend

class CronPlugin(helpers.CategoryPlugin):
    text = 'Cron'
    icon = '/dl/cron/icon.png'
    folder = 'system'

    def on_init(self):
        self._tasks, self._others = backend.read_crontab(self._user)

    def on_session_start(self):
        self._user = shell('whoami').strip()
        backend.fix_crontab(self._user)
        self._labeltext = ''
        self._editing_task = -1
        self._editing_other = -1
        self._error = ''
        self._tasks = []
        self._others = []
        self._tab = 0
        self._show_dialog = 0
        self._show_dialog_user = 0
        self._newtask = False

    def get_ui(self):
        ui = self.app.inflate('cron:main')
        ui.find('tabs').set('active', self._tab)
        user_sel = [UI.SelectOption(text = x, value = x,
                    selected = True if x == self._user else False)
                    for x in backend.get_all_users()]
        ui.appendAll('users_select', *user_sel)

        table_other = ui.find("table_other")
        table_task = ui.find("table_task")
        #Fill non-task strings table
        for i, oth_str in enumerate(self._others):
            table_other.append(UI.DataTableRow(
                    UI.Label(text=oth_str),
                    UI.DataTableCell(
                        UI.HContainer(
                            UI.MiniButton(id='edit_oth/' + str(i),
                                text='Edit'),
                            UI.WarningMiniButton(id='del_oth/' + str(i),
                                text='Delete', msg='Delete a string')
                        ),
                        hidden=True)
                    ))
        #Fill tasks table
        for i, t in enumerate(self._tasks):
            if t.special:
                table_task.append(UI.DataTableRow(
                    UI.Label(text=t.special),
                    UI.Label(), UI.Label(), UI.Label(), UI.Label(),
                    UI.Label(text=t.command),
                    UI.DataTableCell(
                        UI.HContainer(
                            UI.MiniButton(id='edit_task/' + str(i),
                                text='Edit'),
                            UI.WarningMiniButton(id='del_task/' + str(i),
                                text='Delete', msg='Delete a task')
                        ),
                        hidden=True)
                    ))
            else:
                table_task.append(UI.DataTableRow(
                    UI.Label(text=t.m),
                    UI.Label(text=t.h),
                    UI.Label(text=t.dom),
                    UI.Label(text=t.mon),
                    UI.Label(text=t.dow),
                    UI.Label(text=t.command),
                    UI.DataTableCell(
                        UI.HContainer(
                            UI.MiniButton(id='edit_task/' + str(i),
                                text='Edit'),
                            UI.WarningMiniButton(id='del_task/' + str(i),
                                text='Delete', msg='Delete a task')
                        ),
                        hidden=True)
                    ))
        #if crontab return error
        part = self._error.partition(':')[2]
        self._error = 'Error:' + part if part else self._error
        if self._error:
            self.put_message('err', self._error)

        #For tabs name
        REGULARTAB = 11
        ADVANCEDTAB = 12
        SPECIALTAB = 13
        #special values
        avaible_values = ('@reboot', '@hourly', '@daily',
                            '@weekly', '@monthly', '@yearly')
        #edit or new task
        if self._editing_task != -1:
            try:
                task = self._tasks[self._editing_task]
            except IndexError:
                task = backend.Task()
            #edit task
            if not self._newtask:
                ui.remove(str(REGULARTAB))
                if task.special:
                    ui.remove(str(ADVANCEDTAB))
                    ui.find('tabsEdit').set('active', SPECIALTAB)
                    #select special values
                    if task.special and task.special in avaible_values:
                        ui.find('r' + task.special[1:]).\
                            set('checked', 'True')
                    else:
                        ui.find('rreboot').set('checked', 'True')
                    ui.find('s_command').set("value", task.command)
                else:
                    #fill advanced view task
                    ui.find('tabsEdit').set('active', ADVANCEDTAB)
                    ui.remove(str(SPECIALTAB))
                    ui.find('m').set("value", task.m)
                    ui.find('h').set("value", task.h)
                    ui.find('dom').set("value", task.dom)
                    ui.find('mon').set("value", task.mon)
                    ui.find('dow').set("value", task.dow)
                    ui.find('a_command').set("value", task.command)
            #new task
            else:
                ui.find('tabsEdit').set('active', REGULARTAB)
                ui.find('rreboot').set('checked', 'True')
                ui.find('m').set("value", task.m)
                ui.find('h').set("value", task.h)
                ui.find('dom').set("value", task.dom)
                ui.find('mon').set("value", task.mon)
                ui.find('dow').set("value", task.dow)
                #For templates
                ui.find('tabsRegular').set('active', 15)
                SelectOptionNumbs = lambda r: [UI.SelectOption(text=str(m), value=str(m))
                                    for m in xrange(r)]
                #generate similar selectOptions lists for xml.
                minute_select_h = SelectOptionNumbs(60)
                minute_select_d = SelectOptionNumbs(60)
                minute_select_w = SelectOptionNumbs(60)
                minute_select_m = SelectOptionNumbs(60)
                hour_select_d = SelectOptionNumbs(24)
                hour_select_w = SelectOptionNumbs(24)
                hour_select_m = SelectOptionNumbs(24)

                weekday = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                    'Saturday', 'Sunday')
                weekday_select = [UI.SelectOption(text=str(w), value=str(v+1))
                        for v, w in enumerate(weekday)]
                day_select = [UI.SelectOption(text=str(d), value=str(d))
                        for d in range(1, 32)]
                #Fill selects
                ui.appendAll("minute_select_h", *minute_select_h)
                ui.appendAll("minute_select_d", *minute_select_d)
                ui.appendAll("minute_select_w", *minute_select_w)
                ui.appendAll("minute_select_m", *minute_select_m)
                ui.appendAll("hour_select_d", *hour_select_d)
                ui.appendAll("hour_select_w", *hour_select_w)
                ui.appendAll("hour_select_m", *hour_select_m)
                ui.appendAll("weekday_select", *weekday_select)
                ui.appendAll("day_select", *day_select)
        #Nothing happens with task
        else:
            ui.remove('dlgEditTask')
        #edit non-task string
        if self._editing_other != -1 and self._show_dialog:
            other_value = self._others[self._editing_other]\
                if self._editing_other < len(self._others) else ''
            ui.find("other_str").set("value", other_value)
        #Nothing happens with non-task string
        else:
            ui.remove('dlgEditOther')
        return ui

    #noinspection PyUnusedLocal
    @event('minibutton/click')
    @event('button/click')
    @event('linklabel/click')
    def on_click(self, event, params, vars=None):
        "Actions on buttons"
        if params[0] == 'add_task':
            self._editing_task = len(self._tasks)
            self._show_dialog = 1
            self._newtask = True
        if params[0] == 'edit_task':
            self._editing_task = int(params[1])
            self._show_dialog = 1
        if params[0] == 'del_task':
            self._tasks.pop(int(params[1]))
            self._error = backend.write_crontab(self._others +\
                                                self._tasks)
        if params[0] == 'add_oth':
            self._editing_other = len(self._others)
            self._show_dialog = 1
        if params[0] == 'edit_oth':
            self._editing_other = int(params[1])
            self._show_dialog = 1
        if params[0] == 'del_oth':
            self._others.pop(int(params[1]))
            self._error = backend.write_crontab(self._others +\
                                                self._tasks)
            self._tab = 1

#            self._show_dialog_user = 1

    #noinspection PyUnusedLocal
    @event('form/submit')
    def on_submit_form(self, event, params, vars=None):
        "For user select or Regular and advanced Task"
        if params[0] == 'frmUser':
            self._user = vars.getvalue('users_select') or 'root'
            backend.fix_crontab(self._user)
            self._tasks, self._others = backend.read_crontab(self._user)
            return 0
        if params[0] == 'frmAdvanced' and\
                vars.getvalue('action') == 'OK':
            task_str = ' '.join((
                        vars.getvalue('m').replace(' ', '') or '*',
                        vars.getvalue('h').replace(' ', '') or '*',
                        vars.getvalue('dom').replace(' ', '') or '*',
                        vars.getvalue('mon').replace(' ', '') or '*',
                        vars.getvalue('dow').replace(' ', '') or '*'
                        ))
            task_str += '\t' + vars.getvalue('a_command')
            if self.set_task(task_str):
                return 1
        elif params[0] == 'frmSpecial' and\
                vars.getvalue('action') == 'OK':
            task_str = '@' + vars.getvalue('special')
            task_str += '\t' + vars.getvalue('s_command')
            if self.set_task(task_str):
                return 1
        elif params[0] == 'frmTempMinutes' and\
                vars.getvalue('action') == 'OK':
            task_str = '*/' + (vars.getvalue('minutes') or '1')
            task_str += ' * * * *'
            task_str += '\t' + vars.getvalue('command')
            if self.set_task(task_str):
                return 1
        elif params[0] == 'frmTempHours' and\
                vars.getvalue('action') == 'OK':
            task_str = vars.getvalue('minute_select_h') + ' '
            task_str += '*/' + (vars.getvalue('hours')  or '1')
            task_str += ' * * *'
            task_str += '\t' + vars.getvalue('command')
            if self.set_task(task_str):
                return 1
        elif params[0] == 'frmTempDays' and\
                vars.getvalue('action') == 'OK':
            task_str = vars.getvalue('minute_select_d') + ' '
            task_str += vars.getvalue('hour_select_d') + ' '
            task_str += '*/' + (vars.getvalue('days')  or '1')
            task_str += ' * *'
            task_str += '\t' + vars.getvalue('command')
            if self.set_task(task_str):
                return 1
        elif params[0] == 'frmTempMonths' and\
                vars.getvalue('action') == 'OK':
            task_str = vars.getvalue('minute_select_m') + ' '
            task_str += vars.getvalue('hour_select_m') + ' '
            task_str += vars.getvalue('day_select') + ' '
            task_str += '*/' + (vars.getvalue('months')  or '1')
            task_str += ' *'
            task_str += '\t' + vars.getvalue('command')
            if self.set_task(task_str):
                return 1
        elif params[0] == 'frmTempWeek' and\
                vars.getvalue('action') == 'OK':
            task_str = vars.getvalue('minute_select_w') + ' '
            task_str += vars.getvalue('hour_select_w') + ' '
            task_str += '* * '
            task_str += vars.getvalue('weekday_select')
            task_str += '\t' + vars.getvalue('command')
            if self.set_task(task_str):
                return 1
        self._show_dialog = 0
        self._editing_task = -1
        self._newtask = False
        self._tab = 0

    def set_task(self, task_str):
        "Set new or edited task"
        #noinspection PyBroadException
        try:
            new_task = backend.Task(task_str)
        except:
            self._error = 'Error: Wrong options.'
            self._editing_task = -1
            return 1
        if self._editing_task < len(self._tasks):
            self._tasks[self._editing_task] = new_task
        else:
            self._tasks.append(new_task)
        self._error = backend.write_crontab(self._others +\
                                        self._tasks)
        if self._error:
            self._tasks, self._others = backend.read_crontab()
        return 0

    #noinspection PyUnusedLocal
    @event('dialog/submit')
    def on_submit_dlg(self, event, params, vars=None):
        " for submit non-task string. It is use dialog"
        if params[0] == 'dlgEditOther':
            if vars.getvalue('action') == 'OK':
                if self._editing_other < len(self._others):
                    self._others[self._editing_other] = vars.getvalue('other_str')
                else:
                    self._others.append(vars.getvalue('other_str'))
                self._error = backend.write_crontab(self._others +\
                                            self._tasks)
                if self._error:
                    self._tasks, self._others = backend.read_crontab()
            self._show_dialog = 0
            self._editing_other = -1
            self._tab = 1

                
