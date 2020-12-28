"""
Manage all Ajenti core and plugins versions. Check if updates are available and upgrade.
"""

import os
import requests
import shutil
import subprocess
from lxml.html import fromstring
from concurrent import futures

import aj
from jadi import component
from aj.api.http import url, HttpPlugin
from aj.plugins import PluginManager, PluginDependency, BinaryDependency

from aj.api.endpoint import endpoint, EndpointError


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    def __serialize_exception(self, e):
        """
        If a plugin is not loaded, a special exception built with
        PluginDependency.Unsatisfied is thrown.
        This utility function just convert it as dict for angular use.

        :param e: Dependency.Unsatisfied built exception
        :type e: Dependency.Unsatisfied
        :return: Exception informations
        :rtype: dict
        """

        if not e:
            return

        d = {
            'cls': e.__class__.__name__,
            'message': str(e),
            'type': 'generic',
        }

        if isinstance(e, PluginDependency.Unsatisfied):
            d['pluginName'] = e.dependency.plugin_name
            d['type'] = 'PluginDependency.Unsatisfied'

        if isinstance(e, BinaryDependency.Unsatisfied):
            d['binaryName'] = e.dependency.binary_name
            d['type'] = 'BinaryDependency.Unsatisfied'

        return d

    @url(r'/api/plugins/list/installed')
    @endpoint(api=True)
    def handle_api_list_installed(self, http_context):
        """
        Get the plugin list from PluginManager.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of plugin informations, one plugin per dict
        :rtype: list of dict
        """

        r = []
        manager = PluginManager.get(aj.context)
        for name in manager:
            plugin = manager[name]
            r.append({
                'name': plugin['info']['name'],
                'imported': plugin['imported'],
                'crash': self.__serialize_exception(manager.get_crash(plugin['info']['name'])),
                'path': plugin['path'],
                'author': plugin['info']['author'],
                'author_email': plugin['info']['email'],
                'url': plugin['info']['url'],
                'icon': plugin['info']['icon'],
                'version': plugin['info']['version'],
                'title': plugin['info']['title'],
            })
        return r

    @url(r'/api/plugins/pypi/list')
    @endpoint(api=True)
    def handle_api_pypi_list(self, http_context):
        """
        Call pip3 to get list of installed ajenti packages.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of packages
        :rtype: list
        """

        r = {}
        for l in subprocess.check_output(['python3', '-m', 'pip', 'freeze']).splitlines():
            if l:
                package = l.decode().split('=')[0]
                if package:
                    prefix = 'ajenti.plugin.'
                    if package.startswith(prefix):
                        name = package[len(prefix):]
                        r[name] = package
        return r

    @url(r'/api/plugins/pypi/install/(?P<name>.+)/(?P<version>.+)')
    @endpoint(api=True)
    def handle_api_pypi_install(self, http_context, name=None, version=None):
        """
        Install ajenti packages with pip3.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param name: Package name
        :type name: string
        :param version: Version number
        :type version: string
        """

        # TODO replaced with a task
        try:
            subprocess.call(['python3', '-m', 'pip', 'install', 'ajenti.plugin.%s==%s' % (name, version)])
        except subprocess.CalledProcessError as e:
            raise EndpointError(e.output)

    @url(r'/api/plugins/pypi/uninstall/(?P<name>.+)')
    @endpoint(api=True)
    def handle_api_pypi_uninstall(self, http_context, name=None):
        """
        Uninstall ajenti packages with pip3.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param name: Package name
        :type name: string
        """

        try:
            subprocess.check_output(['python3', '-m', 'pip', 'uninstall', '-y', 'ajenti.plugin.%s' % name])
        except subprocess.CalledProcessError as e:
            raise EndpointError(e.output)

    # Deprecated, replaced with handle_api_getpypi_list
    # @url(r'/api/plugins/repo/list')
    # @endpoint(api=True)
    # def handle_api_repo_list(self, http_context):
    #     if os.path.exists('/root/.cache/pip'):
    #         shutil.rmtree('/root/.cache/pip')
    #     try:
    #         return requests.get('https://ajenti.org/plugins/list').json()
    #     except Exception as e:
    #         raise EndpointError(e)

    @url(r'/api/plugins/core/check-upgrade')
    @endpoint(api=True)
    def handle_api_core_check_upgrade(self, http_context):
        """
        Check last published version of ajenti.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Last version number
        :rtype: string
        """

        url = 'https://pypi.python.org/pypi/%s/json' % 'ajenti-panel'
        version = None
        try:
            data = requests.get(url).json()
            version = data['info']['version']
        except Exception as e:
            raise EndpointError(e)
        return version

    @url(r'/api/plugins/getpypi/list')
    @endpoint(api=True)
    def handle_api_getpypi_list(self, http_context):
        """
        Retrieve all necessary ajenti plugin informations from pypi with multiple
        threads.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Plugins list informations, one dict per plugin
        :rtype: list of dict
        """

        def filter_info(plugin):
            """
            Parse all informations from the pypi json package informations.

            :param plugin: Json informations from the packages
            :type plugin: dict
            :return: Parsed informations
            :rtype: dict
            """

            name = plugin['info']['name'].split('.')[-1]
            return {
                "url": plugin['info']['project_urls']['Homepage'],
                "version": plugin['info']['version'],
                "description": plugin['info']['description'],
                "name": name,
                "title": plugin['info']['summary'],
                "author_email": plugin['info']['author_email'],
                "last_month_downloads": plugin['info']['downloads']['last_month'],
                "author": plugin['info']['author'],
                "pypi_name": plugin['info']['name'],
                "type": "official" if name in official else "community",
            }

        def get_json_info(plugin):
            """
            Request plugin informations from pypi and append it to the plugins
            list.

            :param plugin: List of plugins names
            :type plugin: list
            """

            try:
                url = 'https://pypi.python.org/pypi/%s/json' % plugin
                data = requests.get(url).json()
                plugin_list.append(filter_info(data))
            except Exception as e:
                raise EndpointError(e)

        if os.path.exists('/root/.cache/pip'):
            shutil.rmtree('/root/.cache/pip')
        try:
            plugin_list = []
            page = requests.get('https://pypi.org/simple')
            official = requests.get('https://raw.githubusercontent.com/ajenti/ajenti/master/official_plugins.json').json()['plugins']
            pypi_plugin_list = fromstring(page.content).xpath("//a[starts-with(text(),'ajenti.plugin')]/text()")
            with futures.ThreadPoolExecutor(20) as executor:
                res = executor.map(get_json_info, pypi_plugin_list)
            return plugin_list
        except Exception as e:
            raise EndpointError(e)

