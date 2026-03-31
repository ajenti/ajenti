import os
import sys
import logging
import subprocess

from aj.plugins.core.api.tasks import Task


class InstallPlugin (Task):
    name = 'Installing plugin'

    def __init__(self, context, name=None, version=None):
        Task.__init__(self, context)
        self.spec = f'ajenti.plugin.{name}=={version}'

    def run(self):
        if os.getuid() == 0:
            subprocess.check_output([sys.executable, '-m', 'pip', 'install', self.spec])
        else:
            logging.info("Task aborted: no sufficient privileges")


class UpgradeAll (Task):
    name = 'Upgrading Ajenti'

    def run(self):
        if os.getuid() == 0:
            try:
                if sys.executable.startswith('/opt/ajenti'):
                    # Virtualenv install
                    subprocess.check_output(['/opt/ajenti/bin/ajenti-upgrade'])
                else:
                    # Trying with default paths
                    subprocess.check_output(['ajenti-upgrade'])
            except FileNotFoundError as e:
                subprocess.check_output(['/usr/local/bin/ajenti-upgrade'])
        else:
            logging.info("Task aborted: no sufficient privileges")


class UnInstallPlugin (Task):
    name = 'Uninstalling plugin'

    def __init__(self, context, name=None):
        Task.__init__(self, context)
        self.spec = f'ajenti.plugin.{name}'

    def run(self):
        if os.getuid() == 0:
            subprocess.check_output([sys.executable, '-m', 'pip', 'uninstall', '-y', self.spec])
        else:
            logging.info("Task aborted: no sufficient privileges")

