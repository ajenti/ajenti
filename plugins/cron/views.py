from jadi import component

from aj.api.http import url, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint, EndpointError
from .manager import CronManager
from reconfigure.items.crontab import CrontabNormalTaskData, CrontabSpecialTaskData, CrontabEnvSettingData

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    def _create_normal_task(self, values):
        tmp = CrontabNormalTaskData()
        for k,v in values.items():
            setattr(tmp, k, v)
        return tmp

    def _create_special_task(self, values):
        tmp = CrontabSpecialTaskData()
        for k,v in values.items():
            setattr(tmp, k, v)
        return tmp

    def _create_env_settings(self, values):
        tmp = CrontabEnvSettingData()
        for k,v in values.items():
            setattr(tmp, k, v)
        return tmp

    @url(r'/api/get_crontab')
    #@authorize('crontab:show')
    @endpoint(api=True)
    def handle_api_get_crontab(self, http_context):
        if http_context.method == 'GET':
            user = self.context.identity
            crontab = CronManager.get(self.context).load_tab(user)
            return crontab.tree.to_dict()

    @url(r'/api/save_crontab')
    #@authorize('crontab:show')
    @endpoint(api=True)
    def handle_api_save_crontab(self, http_context):
        if http_context.method == 'POST':
            ## Create empty config
            user = self.context.identity
            crontab = CronManager.get(self.context).load_tab(None)
            new_crontab = http_context.json_body()['crontab']
            for _type, values_list in new_crontab.items():
                for values in values_list:
                    if _type == 'normal_tasks':
                        crontab.tree.normal_tasks.append(self._create_normal_task(values))
                    elif _type == 'special_tasks':
                        crontab.tree.special_tasks.append(self._create_special_task(values))
                    elif _type == 'env_settings':
                        crontab.tree.env_settings.append(self._create_env_settings(values))
            try:
                CronManager.get(self.context).save_tab(user, crontab)
                return True
            except Exception as e:
                raise EndpointError(e)