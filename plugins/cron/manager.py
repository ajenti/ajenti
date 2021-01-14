import subprocess

from jadi import service
from reconfigure.configs import CrontabConfig

@service
class CronManager():
    """
    Manage crontab file from user.
    """

    def __init__(self, context):
        self.context = context
        self.crons = {}

    def load_tab(self, user):
        """
        Load crontab file from user.

        :param user: user
        :type user: string
        :return: CrontabConfig
        :rtype: object
        """

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
        """
        Save new crontab data into crontab file.

        :param user: user
        :type user: string
        :param config: CrontabConfig
        :type config: CrontabConfig
        """

        data = config.save()[None].encode()
        p = subprocess.Popen(['crontab', '-', '-u', user])
        stdout, stderr = p.communicate(data + b'\n')
        if stderr:
            raise Exception(stderr)