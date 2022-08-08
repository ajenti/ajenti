"""
Module to handle an user crontab file.
"""

import os
import pwd
from jadi import component

from aj.api.http import get, post, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError
from .manager import CronManager
from reconfigure.items.crontab import CrontabNormalTaskData, CrontabSpecialTaskData, CrontabEnvSettingData

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @get(r'/api/crontab')
    @endpoint(api=True)
    def handle_api_get_crontab(self, http_context):
        """
        Get the cron content through ConManager and store it in a dict.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Cron jobs
        :rtype: dict
        """

        user = pwd.getpwuid(os.getuid()).pw_name
        crontab = CronManager.get(self.context).load_tab(user)
        return crontab.tree.to_dict()

    @post(r'/api/crontab')
    @endpoint(api=True)
    def handle_api_save_crontab(self, http_context):
        """
        Store cron data from frontend in a cron file through CronManager.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: True if successful
        :rtype: bool
        """

        def setTask(obj, values):
            for k,v in values.items():
                setattr(obj, k, v)
            return obj

        # Create empty config
        user = self.context.identity
        crontab = CronManager.get(self.context).load_tab(None)
        new_crontab = http_context.json_body()['crontab']
        for _type, values_list in new_crontab.items():
            for values in values_list:
                if _type == 'normal_tasks':
                    crontab.tree.normal_tasks.append(setTask(CrontabNormalTaskData(), values))
                elif _type == 'special_tasks':
                    crontab.tree.special_tasks.append(setTask(CrontabSpecialTaskData(), values))
                elif _type == 'env_settings':
                    crontab.tree.env_settings.append(setTask(CrontabEnvSettingData(), values))
        try:
            CronManager.get(self.context).save_tab(user, crontab)
            return True
        except Exception as e:
            raise EndpointError(e)