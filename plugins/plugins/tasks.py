import subprocess

from aj.plugins.core.api.tasks import Task


class InstallPlugin (Task):
    name = 'Installing plugin'

    def __init__(self, context, name=None, version=None):
        Task.__init__(self, context)
        self.spec = 'ajenti.plugin.%s==%s' % (name, version)

    def run(self):
        subprocess.check_output(['pip', 'install', self.spec])


class UpgradeAll (Task):
    name = 'Upgrading Ajenti'

    def run(self):
        try:
            subprocess.check_output(['ajenti-upgrade'])
        except:
            subprocess.check_output(['/usr/local/bin/ajenti-upgrade'])
