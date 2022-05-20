import sys
import subprocess

from aj.plugins.core.api.tasks import Task


class InstallPlugin (Task):
    name = 'Installing plugin'

    def __init__(self, context, name=None, version=None):
        Task.__init__(self, context)
        self.spec = f'ajenti.plugin.{name}=={version}'

    def run(self):
        subprocess.check_output([sys.executable, '-m', 'pip', 'install', self.spec])


class UpgradeAll (Task):
    name = 'Upgrading Ajenti'

    def run(self):
        try:
            subprocess.check_output(['ajenti-upgrade'])
        except FileNotFoundError as e:
            subprocess.check_output(['/usr/local/bin/ajenti-upgrade'])


class UnInstallPlugin (Task):
    name = 'Uninstalling plugin'

    def __init__(self, context, name=None):
        Task.__init__(self, context)
        self.spec = f'ajenti.plugin.{name}'

    def run(self):
        subprocess.check_output([sys.executable, '-m', 'pip', 'uninstall', '-y', self.spec])

