import subprocess

from jadi import service
from reconfigure.configs import CrontabConfig

@service
class CronManager():
    def __init__(self, context):
        self.context = context
        self.crons = {}

    def load_tab(self, user):
        if user is None:
            data = ''
        else:
            try:
                data = subprocess.check_output(['crontab', '-l', '-u', user])
            except Exception:
                data = ''
        config = CrontabConfig(content=data)
        config.load()
        return config

    def save_tab(self, user, config):
        data = config.save()[None].encode()
        p = subprocess.Popen(['crontab', '-', '-u', user])
        stdout, stderr = p.communicate(data + b'\n')
        if stderr:
            raise Exception(stderr)