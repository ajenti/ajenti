import logging

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

        def create_task(cls):
            logging.info('[cron] created a %s' % cls.__name__)
            return cls()

        def remove_task(i, c):
            c.remove(i)
            logging.info('[cron] removed %s' % getattr(i, 'command', None))

        self.binder = Binder(None, self.find('config'))
        self.find('normal_tasks').new_item = lambda c: create_task(CrontabNormalTaskData)
        self.find('special_tasks').new_item = lambda c: create_task(CrontabSpecialTaskData)
        self.find('env_settings').new_item = lambda c: create_task(CrontabEnvSettingData)
        self.find('normal_tasks').delete_item = remove_task
        self.find('special_tasks').delete_item = remove_task
        self.find('env_settings').delete_item = remove_task

        self.current_user = 'root'

    def on_page_load(self):
        self.refresh()

    @on('user-select', 'click')
    def on_user_select(self):
        self.current_user = self.find('users').value
        logging.info('[cron] selected user %s' % self.current_user)
        self.refresh()

    def refresh(self):
        users_select = self.find('users')
        users_select.value = self.current_user
        users = [x.name for x in PasswdConfig(path='/etc/passwd').load().tree.users]
        users_select.values = users_select.labels = users

        self.config = CronManager.get().load_tab(self.current_user)
        self.binder.setup(self.config.tree).populate()

    @on('save', 'click')
    def on_save(self):
        self.binder.update()
        logging.info('[cron] edited tasks')
        try:
            CronManager.get().save_tab(self.current_user, self.config)
            self.refresh()
        except Exception as e:
            self.context.notify('error', e.message)
