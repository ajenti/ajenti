try:
    import xmlrpclib
except ImportError:
    import xmlrpc.client as xmlrpclib

import pkg_resources
import importlib

from jadi import component
from aj.plugins.packages.api import PackageManager, Package


@component(PackageManager)
class PIPPackageManager(PackageManager):
    """
    Manager to handle pip packages.
    """

    id = 'pip'
    name = 'PIP'

    def __init__(self, context):
        PackageManager.__init__(self, context)
        self.client = xmlrpclib.ServerProxy('https://pypi.python.org/pypi')

    def __make_package_pipdist(self, dist):
        """
        Convert pip package object in package object.

        :param apt_package: Pip package object from apt module
        :type apt_package: Pip package object from apt module
        :return: Package object
        :rtype: Package object
        """

        p = Package(self)
        p.id = '%s==%s' % (dist.key, dist.version)
        p.name = dist.key
        p.version = dist.version
        p.description = None
        p.is_installed = True
        p.installed_version = dist.version
        return p

    def __make_package(self, dist):
        """
        Convert pip package object in package object.

        :param apt_package: Pip package object from apt module
        :type apt_package: Pip package object from apt module
        :return: Package object
        :rtype: Package object
        """

        p = Package(self)
        p.id = '%s==%s' % (dist['name'], dist['version'])
        p.name = dist['name']
        p.version = dist['version']
        p.description = dist['summary']
        importlib.reload(pkg_resources)
        for d in pkg_resources.working_set:
            if d.key == p.name:
                p.is_installed = True
                p.installed_version = d.version
                p.is_upgradeable = p.installed_version != p.version
        return p

    def list(self, query=None):
        """
        Generator for all packages.

        :param query: Search string
        :type query: string
        :return: Package object
        :rtype:Package object
        """

        for dist in self.client.search({'name': query}):
            yield self.__make_package(dist)

    def get_package(self, _id):
        """
        Get package informations.

        :param _id: Package name
        :type _id: string
        :return: Package object
        :rtype: Package object
        """

        for d in pkg_resources.working_set:
            if d.key == _id.split('==')[0]:
                return self.__make_package_pipdist(d)

    def update_lists(self, progress_callback):
        """
        Refresh list of packages.

        :param progress_callback: Callback function to follow progress
        :type progress_callback: function
        """

        pass

    def get_apply_cmd(self, selection):
        """
        Prepare command to apply.

        :param selection: Dict of packages an actions
        :type selection: dict
        :return: Command for terminal use
        :rtype: string
        """

        packages = []
        cmd = ''

        for sel in selection:
            if sel['operation'] in ['install', 'upgrade']:
                packages.append(sel['package']['id'])
        if packages:
            cmd = 'python3 -m pip install ' + ' '.join(packages) + ' ;'
            packages = []

        for sel in selection:
            if sel['operation'] in ['remove']:
                packages.append(sel['package']['name'])
        if packages:
            cmd = 'python3 -m pip uninstall ' + ' '.join(packages)
        return cmd
