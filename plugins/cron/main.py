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
        self._newtask = False

        #self._user = ''

    def get_ui(self):
        ui = self.app.inflate('cron:main')
        ui.find('tabs').set('active', self._tab)
        user_sel = [UI.SelectOption(text = x, value = x,
                    selected = True if x == self._user else False)
                    for x in backend.get_all_users()]
        ui.appendAll("users_select", *user_sel)
        self.put_message('info',
                         '{0} tasks for {1}'.format(len(self._tasks), self._user))
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

        part = self._error.partition(':')[2]
        self._error = 'Error:' + part if part else self._error
        if self._error:
            self.put_message('err', self._error)

        REGULARTAB = 11
        ADVANCEDTAB = 12
        SPECIALTAB = 13
        avaible_values = ('@reboot', '@hourly', '@daily',
                            '@weekly', '@monthly', '@yearly')
        if self._editing_task != -1:
            try:
                task = self._tasks[self._editing_task]
            except IndexError:
                task = backend.Task()

            if not self._newtask:
                ui.remove(str(REGULARTAB))
                if task.special:
                    ui.remove(str(ADVANCEDTAB))
                    ui.find('tabsEdit').set('active', SPECIALTAB)

                    if task.special and task.special in avaible_values:
                        ui.find('r' + task.special[1:]).\
                            set('checked', 'True')
                    else:
                        ui.find('rreboot').set('checked', 'True')
                else:
                    ui.find('tabsEdit').set('active', ADVANCEDTAB)
                    ui.remove(str(SPECIALTAB))
                    ui.find('m').set("value", task.m)
                    ui.find('h').set("value", task.h)
                    ui.find('dom').set("value", task.dom)
                    ui.find('mon').set("value", task.mon)
                    ui.find('dow').set("value", task.dow)
                    ui.find('command').set("value", task.command)
            else:
                ui.find('tabsEdit').set('active', REGULARTAB)
                ui.find('rreboot').set('checked', 'True')
                ui.find('m').set("value", task.m)
                ui.find('h').set("value", task.h)
                ui.find('dom').set("value", task.dom)
                ui.find('mon').set("value", task.mon)
                ui.find('dow').set("value", task.dow)
                ui.find('command').set("value", task.command)
                #For templates
                ui.find('tabsRegular').set('active', 15)
                minute_select_h = [UI.SelectOption(text=str(m), value=str(m))
                                    for m in xrange(60)]
                minute_select_d = minute_select_h[:]
                print minute_select_d[0]
                print minute_select_h[0]
                hour_select = [UI.SelectOption(text=str(h), value=str(h))
                                    for h in xrange(24)]
                ui.appendAll("minute_select_h", *minute_select_h)
                ui.appendAll("minute_select_d", *minute_select_h)
                ui.appendAll("hour_select", *hour_select)



            

        else:
            ui.remove('dlgEditTask')
        if self._editing_other != -1 and self._show_dialog:
            other_value = self._others[self._editing_other]\
                if self._editing_other < len(self._others) else ''
            ui.find("other_str").set("value", other_value)
            
        else:
            ui.remove('dlgEditOther')
#        if self._editing_task != -1:
#            try:
#                task = self._tasks[self._editing_task]
#            except IndexError:
#                task = backend.Task()
#            if self._show_dialog:
#                ui.append(self.get_ui_edit(task))
#        if self._editing_other != -1 and self._show_dialog:
#            ui.append(self.get_ui_edit_other())
        return ui

#    def get_default_ui(self):
#
#        tabbar.add("Tasks", vbox_task)
#        tabbar.add("Non-task strings", vbox_oth)
#        vbox = UI.VContainer(topbox, tabbar)
#        if self._editing_task != -1:
#            try:
#                task = self._tasks[self._editing_task]
#            except IndexError:
#                task = backend.Task()
#            if self._show_dialog:
#                vbox.append(self.get_ui_edit(task))
#        if self._editing_other != -1 and self._show_dialog:
#            vbox.append(self.get_ui_edit_other())
#        return vbox

#    def get_ui_edit_other(self):
#        other_value = self._others[self._editing_other]\
#            if self._editing_other < len(self._others) else ''
#        vbox = UI.VContainer(UI.Label(text="Edit string", size=2),
#                            UI.TextInput(value=other_value, name='other_str'))
#        dlg = UI.DialogBox(
#                vbox,
#                title='Edit non-task string',
#                id='dlgEditOther')
#        return dlg

    def get_ui_edit(self, t):
        pass
#        tabbar = UI.TabControl()
#        if self._newtask:
#            tabbar.add('Regular', self.get_ui_template())
#        if self._newtask or not t.special:
#            tabbar.add('Advanced', self.get_ui_advanced(t))
#        if self._newtask or t.special:
#            tabbar.add('Special', self.get_ui_special(t))
#        dlg = UI.DialogBox(
#                tabbar,
#                title='Edit task',
#                id='dlgEditTask',
#                hideok=True,
#                hidecancel=True
#              )
#        return dlg

#    def get_ui_advanced(self, t):
#        ui.find('m').set("value", t.m)
#        ui.find('h').set("value", t.h)
#        ui.find('dom').set("value", t.dom)
#        ui.find('mon').set("value", t.mon)
#        ui.find('dow').set("value", t.dow)
#        ui.find('command').set("value", t.command)
#
#        return UI.FormBox(adv_table, id='frmAdvanced')

    def get_ui_special(self, t):
        avaible_values = ('@reboot', '@hourly', '@daily',
                            '@weekly', '@monthly', '@yearly')
        if t.special and t.special in avaible_values:
            index = avaible_values.index(t.special)
        else:
            index = 0
        spc_table = UI.LayoutTable(
                    UI.LayoutTableRow(
                        UI.Radio(value='reboot', text='On reboot',
                                name='special',
                                checked=(index == 0)),
                        UI.Radio(value='hourly', text='Hourly',
                                name='special',
                                checked=(index == 1))),
                    UI.LayoutTableRow(
                        UI.Radio(value='daily', text='Daily',
                                name='special',
                                checked=(index == 2)),
                        UI.Radio(value='weekly', text='Weekly',
                                name='special',
                                checked=(index == 3))),
                    UI.LayoutTableRow(
                        UI.Radio(value='monthly', text='Monthly',
                                name='special',
                                checked=(index == 4)),
                        UI.Radio(value='yearly', text='Yearly',
                                name='special',
                                checked=(index == 5))),
                    UI.LayoutTableRow(
                            UI.Label(text='Command'),
                            UI.TextInput(name='command',
                                        value=t.command)
                    ))
        return UI.FormBox(spc_table, id='frmSpecial')

    def get_ui_template(self):
        tabbar = UI.TabControl()
        tabbar.add('Minutely', self.get_ui_temp_minutely())
        tabbar.add('Hourly', self.get_ui_temp_hourly())
        tabbar.add('Daily', self.get_ui_temp_daily())
        tabbar.add('Weekly', self.get_ui_temp_weekly())
        tabbar.add('Monthly', self.get_ui_temp_monthly())
        return tabbar

    def get_ui_temp_minutely(self):
        temp_table = UI.VContainer(
                    UI.HContainer(
                        UI.Label(text='Start task every'),
                        UI.TextInput(name='minutes', size='3'),
                        UI.Label(text='minutes')
                    ),
                    UI.HContainer(
                        UI.Label(text='Command'),
                        UI.TextInput(name='command', size='30'),
                        )
                    )
        return UI.FormBox(temp_table, id='frmTempMinutes')

    def get_ui_temp_hourly(self):
        minute_select = [UI.SelectOption(text=str(m), value=str(m))
                        for m in range(60)]
        temp_table = UI.VContainer(
                    UI.HContainer(
                        UI.Label(text='Start task every'),
                        UI.TextInput(name='hours', size='3'),
                        UI.Label(text='hours'),
                        UI.Label(text='at'),
                        UI.Select(*minute_select, name='minutes'),
                        UI.Label(text='minutes')
                    ),
                    UI.HContainer(
                        UI.Label(text='Command'),
                        UI.TextInput(name='command', size='30')
                        )
                    )
        return UI.FormBox(temp_table, id='frmTempHours')

    def get_ui_temp_daily(self):
        hour_select = [UI.SelectOption(text=str(h), value=str(h))
                        for h in range(24)]
        minute_select = [UI.SelectOption(text=str(m), value=str(m))
                        for m in range(60)]
        temp_table = UI.VContainer(
                    UI.HContainer(
                        UI.Label(text='Start task every'),
                        UI.TextInput(name='days', size='3'),
                        UI.Label(text='days'),
                        UI.Label(text='at'),
                        UI.Select(*hour_select, name='hour'),
                        UI.Label(text=':'),
                        UI.Select(*minute_select, name='minute')
                    ),
                    UI.HContainer(
                        UI.Label(text='Command'),
                        UI.TextInput(name='command', size='30')
                    ))
        return UI.FormBox(temp_table, id='frmTempDays')

    def get_ui_temp_weekly(self):
        weekday = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                    'Saturday', 'Sunday')
        hour_select = [UI.SelectOption(text=str(h), value=str(h))
                        for h in range(24)]
        minute_select = [UI.SelectOption(text=str(m), value=str(m))
                        for m in range(60)]
        weekday_select = [UI.SelectOption(text=str(w), value=str(v+1))
                        for v, w in enumerate(weekday)]
        temp_table = UI.VContainer(
                    UI.HContainer(
                        UI.Label(text='Start task every'),
                        UI.Select(*weekday_select, name='weekday'),
                        UI.Label(text='at'),
                        UI.Select(*hour_select, name='hour'),
                        UI.Label(text=':'),
                        UI.Select(*minute_select, name='minute')
                    ),
                    UI.HContainer(
                        UI.Label(text='Command'),
                        UI.TextInput(name='command', size='30')
                    ))
        return UI.FormBox(temp_table, id='frmTempWeek')

    def get_ui_temp_monthly(self):
        hour_select = [UI.SelectOption(text=str(h), value=str(h))
                        for h in range(24)]
        minute_select = [UI.SelectOption(text=str(m), value=str(m))
                        for m in range(60)]
        day_select = [UI.SelectOption(text=str(d), value=str(d))
                        for d in range(1, 32)]
        temp_table = UI.VContainer(
                    UI.HContainer(
                        UI.Label(text='Start task every'),
                        UI.TextInput(name='months', size='3'),
                        UI.Label(text='months')
                    ),
                    UI.HContainer(
                        UI.Label(text='On'),
                        UI.Select(*day_select, name='day'),
                        UI.Label(text='th at'),
                        UI.Select(*hour_select, name='hour'),
                        UI.Label(text=':'),
                        UI.Select(*minute_select, name='minute')
                    ),
                    UI.HContainer(
                        UI.Label(text='Command'),
                        UI.TextInput(name='command', size='30')
                    ))
        return UI.FormBox(temp_table, id='frmTempMonths')

    @event('minibutton/click')
    @event('button/click')
    @event('linklabel/click')
    def on_click(self, event, params, vars=None):
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
        #if params[0] == 'ch_user':
        #    self._user = vars.getvalue('users') or 'root'
        #    print self._user
            #self._show_dialog = 1
            #self._newtask = True
        
    @event('form/submit')
    def on_submit_form(self, event, params, vars=None):
        if params[0] == 'frmUsers' and\
                vars.getvalue('action') == 'OK':
            print vars
            self._user = vars.getvalue('users_select') or 'root'
            backend.fix_crontab(self._user)
            self._tasks, self._others = backend.read_crontab(self._user)
            print self._user
        if params[0] == 'frmAdvanced' and\
                vars.getvalue('action') == 'OK':
            print "Advanced"
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
            task_str += vars.getvalue('hour_select') + ' '
            task_str += '*/' + (vars.getvalue('days')  or '1')
            task_str += ' * *'
            task_str += '\t' + vars.getvalue('command')
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
            if self.set_task(task_str):
                return 1
        elif params[0] == 'frmTempWeek' and\
                vars.getvalue('action') == 'OK':
            task_str = vars.getvalue('minute') + ' '
            task_str += vars.getvalue('hour') + ' '
            task_str += '* * '
            task_str += vars.getvalue('weekday')
            task_str += '\t' + vars.getvalue('command')
            if self.set_task(task_str):
                return 1
        self._show_dialog = 0
        self._editing_task = -1
        self._newtask = False

    def set_task(self, task_str):
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

    @event('dialog/submit')
    def on_submit_dlg(self, event, params, vars=None):
        if params[0] == 'dlgEditOther' and\
                vars.getvalue('action') == 'OK':
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
                
