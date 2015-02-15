import subprocess

from aj.plugins.core.api.tasks import Task


class InstallPlugin (Task):
    name = 'Installing plugin'

    def __init__(self, context, name=None, version=None):
        Task.__init__(self, context)
        self.spec = 'ajenti.plugin.%s==%s' % (name, version)

    def run(self):
        try:
            subprocess.check_output(['pip', 'install', self.spec])
            self.push('plugins', 'install-done')
        except subprocess.CalledProcessError as e:
            self.push('plugins', 'install-error')
