import sys
import pkg_resources
import importlib
from requests import Session
from bs4 import BeautifulSoup

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

    def __make_package_pipdist(self, dist):
        """
        Convert pip package object in package object.

        :param apt_package: Pip package object from apt module
        :type apt_package: Pip package object from apt module
        :return: Package object
        :rtype: Package object
        """

        p = Package(self)
        p.id = f'{dist.key}=={dist.version}'
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
        p.id = f'{dist["name"]}=={dist["version"]}'
        p.name = dist['name']
        p.version = dist['version']
        p.description = dist['summary']
        p.created = dist['created']
        importlib.reload(pkg_resources)
        for d in pkg_resources.working_set:
            if d.key == p.name:
                p.is_installed = True
                p.installed_version = d.version
                p.is_upgradeable = p.installed_version != p.version
        return p

    def __requests_pypi_search(self, query):
        """
        Launch a query on pypi search and filter the results with bs4.
        Heavily inspired from https://github.com/victorgarric/pip_search/blob/master/pip_search/pip_search.py

        :param query: string to search for
        :type query: string
        :return:
        :rtype:
        """

        api_url = 'https://pypi.org/search/'
        session = Session()

        packages = []
        snippets = []
        for page in range(1,3):
            params = {'q': query, 'page': page}
            result = session.get(api_url, params=params)

            soup = BeautifulSoup(result.text, 'html.parser')
            snippets += soup.select('a[class*="snippet"]')

        for snippet in snippets:
            package = {}
            for value in ["name", "version", "created"]:
                package[value] = snippet.select_one(f'span[class*="{value}"]').text.strip()
            package['summary'] = snippet.select_one(f'p[class*="description"]').text.strip()
            packages.append(package)

        return packages

    def list(self, query=None):
        """
        Generator for all packages.

        :param query: Search string
        :type query: string
        :return: Package object
        :rtype:Package object
        """

        for dist in self.__requests_pypi_search(query):
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
            cmd = f'{sys.executable} -m pip install {" ".join(packages)} ;'
            packages = []

        for sel in selection:
            if sel['operation'] in ['remove']:
                packages.append(sel['package']['name'])
        if packages:
            cmd = f'{sys.executable} -m pip uninstall {" ".join(packages)}'
        return cmd
