import os
import requests
import shutil
import subprocess
from bs4 import BeautifulSoup as bs
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
        # TODO replaced with a task
        try:
            subprocess.call(['python3', '-m', 'pip', 'install', 'ajenti.plugin.%s==%s' % (name, version)])
        except subprocess.CalledProcessError as e:
            raise EndpointError(e.output)

    @url(r'/api/plugins/pypi/uninstall/(?P<name>.+)')
    @endpoint(api=True)
    def handle_api_pypi_uninstall(self, http_context, name=None):
        try:
            subprocess.check_output(['python3', '-m', 'pip', 'uninstall', '-y', 'ajenti.plugin.%s' % name])
        except subprocess.CalledProcessError as e:
            raise EndpointError(e.output)

    @url(r'/api/plugins/repo/list')
    @endpoint(api=True)
    def handle_api_repo_list(self, http_context):
        if os.path.exists('/root/.cache/pip'):
            shutil.rmtree('/root/.cache/pip')
        try:
            return requests.get('http://ajenti.org/plugins/list').json()
        except Exception as e:
            raise EndpointError(e)

    @url(r'/api/plugins/core/check-upgrade')
    @endpoint(api=True)
    def handle_api_core_check_upgrade(self, http_context):
        url = 'https://pypi.python.org/pypi/%s/json' % 'ajenti-panel'
        try:
            data = requests.get(url).json()
        except Exception as e:
            raise EndpointError(e)
        version = data['info']['version']
        if version != aj.version:
            return version
        return None

    @url(r'/api/plugins/testpypi/list')
    @endpoint(api=True)
    def handle_api_testpypi_list(self, http_context):
        def filter_aj(tag):
            return tag.name == 'a' and tag.text.startswith('ajenti.plugin')

        def get_json_info(plugin):
            try:
                url = 'https://pypi.python.org/pypi/%s/json' % plugin
                data = requests.get(url).json()
                plugin_list.append(data)
            except Exception as e:
                raise EndpointError(e)

        if os.path.exists('/root/.cache/pip'):
            shutil.rmtree('/root/.cache/pip')
        try:
            plugin_list = []
            page = requests.get('https://pypi.org/simple')
            soup = bs(page.text, 'html.parser')
            to_get = ["aj", "ajenti-panel", "ajenti-dev-multitool"] + [plugin.text for plugin in soup.find_all(filter_aj)]
            with futures.ThreadPoolExecutor(20) as executor:
                res = executor.map(get_json_info, to_get)
            return plugin_list
        except Exception as e:
            raise EndpointError(e)

