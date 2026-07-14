import os
import re
import sys
import logging
import subprocess

from aj.plugins.core.api.tasks import Task

_SAFE_NAME = re.compile(r'^[A-Za-z0-9]([A-Za-z0-9._-]*[A-Za-z0-9])?$')
_SAFE_VERSION = re.compile(r'^[A-Za-z0-9]([A-Za-z0-9.+_-]*[A-Za-z0-9])?$')


def _check_spec_parts(name, version=None):
    if not (name and _SAFE_NAME.match(name)):
        raise ValueError(f'Refusing malformed package name {name!r}')
    if version is not None and not (version and _SAFE_VERSION.match(version)):
        raise ValueError(f'Refusing malformed package version {version!r}')


class InstallPlugin (Task):
    name = 'Installing plugin'

    def __init__(self, context, name=None, version=None):
        Task.__init__(self, context)
        _check_spec_parts(name, version)
        self.spec = f'ajenti.plugin.{name}=={version}'

    def run(self):
        if os.getuid() == 0:
            subprocess.check_output([
                sys.executable, '-m', 'pip', 'install',
                '--no-deps', '--index-url', 'https://pypi.org/simple/',
                '--', self.spec,
            ])
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
        _check_spec_parts(name)
        self.spec = f'ajenti.plugin.{name}'

    def run(self):
        if os.getuid() == 0:
            subprocess.check_output([sys.executable, '-m', 'pip', 'uninstall', '-y', self.spec])
        else:
            logging.info("Task aborted: no sufficient privileges")

