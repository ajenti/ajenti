import subprocess

from ajenti.api import plugin
from reconfigure.configs import CrontabConfig


@plugin
class CronManager (object):
    def load_tab(self, user):
        self.current_user = user
        try:
            data = subprocess.check_output(['crontab', '-l', '-u', user])
        except Exception:
            data = ''
        config = CrontabConfig(content=data)
        config.load()
        return config

    def save_tab(self, user, config):
        data = config.save()[None]
        p = subprocess.Popen(['crontab', '-', '-u', user])
        stdout, stderr = p.communicate(data + '\n')
        if stderr:
            raise Exception(stderr)
            
