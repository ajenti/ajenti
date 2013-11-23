from ajenti.api import *
from ajenti.ui.binder import Binder
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on

from reconfigure.configs import PasswdConfig
from reconfigure.items.crontab import CrontabEnvSettingData, CrontabNormalTaskData, CrontabSpecialTaskData

from api import CronManager


@plugin
class Cron (SectionPlugin):
    def init(self):
        self.title = 'Cron'
        self.icon = 'time'
        self.category = _('System')
        self.append(self.ui.inflate('cron:main'))

        self.binder = Binder(None, self.find('config'))
        self.find('normal_tasks').new_item = lambda c: CrontabNormalTaskData()
        self.find('special_tasks').new_item = lambda c: CrontabSpecialTaskData()
        self.find('env_settings').new_item = lambda c: CrontabEnvSettingData()

        self.current_user = 'root'

    def on_page_load(self):
        self.refresh()

    @on('user-select', 'click')
    def on_user_select(self):
        self.current_user = self.find('users').value
        self.refresh()

    def refresh(self):
        users_select = self.find('users')
        users_select.value = self.current_user
        users = [x.name for x in PasswdConfig(path='/etc/passwd').load().tree.users if int(x.uid) >= 500 or x.name == 'root']
        users_select.values = users_select.labels = users

        self.config = CronManager.get().load_tab(self.current_user)
        self.binder.reset(self.config.tree).autodiscover().populate()

    @on('save', 'click')
    def on_save(self):
        self.binder.update()
        try:
            CronManager.get().save_tab(self.current_user, self.config)
            self.refresh()
        except Exception, e:
            self.context.notify('error', e.message)
