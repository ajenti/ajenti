import re
import sys
import importlib.metadata
from concurrent.futures import ThreadPoolExecutor
from requests import Session

from jadi import component
from aj.plugins.packages.api import PackageManager, Package


@component(PackageManager)
class PIPPackageManager(PackageManager):
    """
    Manager to handle pip packages.
    """

    id = 'pip'
    name = 'PIP'

    PYPI_SIMPLE_URL = 'https://pypi.org/simple/'
    PYPI_JSON_URL = 'https://pypi.org/pypi/{name}/json'
    MAX_RESULTS = 20
    PACKAGE_ID_RE = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_\-\.]*(\[[a-zA-Z0-9_,]+\])?==[a-zA-Z0-9][a-zA-Z0-9\.\-]*$')
    PACKAGE_NAME_RE = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_\-\.]*$')

    def __init__(self, context):
        PackageManager.__init__(self, context)
        self._session = Session()

    def __make_package_pipdist(self, dist):
        """
        Convert pip package object in package object.

        :param apt_package: Pip package object from apt module
        :type apt_package: Pip package object from apt module
        :return: Package object
        :rtype: Package object
        """

        p = Package(self)
        p.id = f'{dist.name}=={dist.version}'
        p.name = dist.name
        p.version = dist.version
        p.description = None
        p.is_installed = True
        p.installed_version = dist.version
        return p

    def __make_package(self, info, urls):
        """
        Convert PyPI JSON API response into a Package object.

        :param info: info block from PyPI JSON API response
        :type info: dict
        :param urls: urls block from PyPI JSON API response
        :type urls: list
        :return: Package object
        :rtype: Package object
        """

        p = Package(self)
        p.id = f'{info["name"]}=={info["version"]}'
        p.name = info['name']
        p.version = info['version']
        p.description = info['summary']
        p.created = urls[0]['upload_time'] if urls else None
        for d in importlib.metadata.distributions():
            if d.name and d.name.lower().replace('-', '_') == info['name'].lower().replace('-', '_'):
                p.is_installed = True
                p.installed_version = d.version
                p.is_upgradeable = p.installed_version != p.version
        return p

    def __fetch_pypi_metadata(self, name):
        try:
            resp = self._session.get(self.PYPI_JSON_URL.format(name=name), timeout=10)
            return resp.json()
        except Exception:
            return None

    def __search_pypi(self, query):
        """
        Search packages on PyPI using the Simple API (PEP 691).

        :param query: Search string
        :type query: string
        :return: List of matching package names, capped at MAX_RESULTS
        :rtype: list
        """

        resp = self._session.get(
            self.PYPI_SIMPLE_URL,
            headers={'Accept': 'application/vnd.pypi.simple.v1+json'},
            timeout=30,
        )
        q = query.lower()
        matches = [
            p['name'] for p in resp.json()['projects']
            if q in p['name'].lower()
        ]

        def relevance(name):
            n = name.lower()
            if n == q:
                return 0
            if n.startswith(q):
                return 1
            return 2

        matches.sort(key=relevance)
        return matches[:self.MAX_RESULTS]

    def list(self, query=None):
        """
        Generator for all packages.

        :param query: Search string
        :type query: string
        :return: Package object
        :rtype:Package object
        """

        with ThreadPoolExecutor(max_workers=8) as executor:
            results = executor.map(self.__fetch_pypi_metadata, self.__search_pypi(query))
        for data in results:
            if not data or 'info' not in data:
                continue
            yield self.__make_package(data['info'], data.get('urls', []))

    def get_package(self, _id):
        """
        Get package informations.

        :param _id: Package name
        :type _id: string
        :return: Package object
        :rtype: Package object
        """

        for d in importlib.metadata.distributions():
            if d.name == _id.split('==')[0]:
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
                pkg_id = sel['package']['id']
                if self.PACKAGE_ID_RE.match(pkg_id):
                    packages.append(pkg_id)
        if packages:
            cmd = f'{sys.executable} -m pip install {" ".join(packages)} ;'
            packages = []

        for sel in selection:
            if sel['operation'] in ['remove']:
                pkg_name = sel['package']['name']
                if self.PACKAGE_NAME_RE.match(pkg_name):
                    packages.append(pkg_name)
        if packages:
            cmd = f'{sys.executable} -m pip uninstall {" ".join(packages)}'
        return cmd
