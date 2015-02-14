import json
import subprocess
import urllib3

import aj
from aj.api import *
from aj.api.http import url, HttpPlugin
from aj.plugins import PluginManager

from aj.plugins.core.api.endpoint import endpoint, EndpointError


@component(HttpPlugin)
class Handler (HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/plugins/list/installed')
    @endpoint(api=True)
    def handle_api_list_installed(self, http_context):
        r = []
        for plugin in PluginManager.get(aj.context).get_all().values():
            r.append({
                'name': plugin.name,
                'active': plugin.active,
                'crash': plugin.crash,
                'path': plugin.path,
                'author': plugin.author,
                'author_email': plugin.email,
                'url': plugin.url,
                'icon': plugin.icon,
                'version': plugin.version,
                'title': plugin.title,
            })
        return r


    @url(r'/api/plugins/pypi/list')
    @endpoint(api=True)
    def handle_api_pypi_list(self, http_context):
        r = {}
        for l in subprocess.check_output(['pip', 'freeze']).splitlines():
            if l:
                package = l.split('=')[0]
                if package:
                    prefix = 'ajenti.plugin.'
                    if package.startswith(prefix):
                        name = package[len(prefix):]
                        r[name] = package
        return r

    @url(r'/api/plugins/pypi/install/(?P<name>.+)')
    @endpoint(api=True)
    def handle_api_pypi_install(self, http_context, name=None):
        if subprocess.call(['pip', 'install', '-U', 'ajenti.plugin.%s' % name]) != 0:
            raise EndpointError('PIP returned error')

    @url(r'/api/plugins/pypi/uninstall/(?P<name>.+)')
    @endpoint(api=True)
    def handle_api_pypi_uninstall(self, http_context, name=None):
        if subprocess.call(['pip', 'uninstall', '-y', 'ajenti.plugin.%s' % name]) != 0:
            raise EndpointError('PIP returned error')

    @url(r'/api/plugins/repo/list')
    @endpoint(api=True)
    def handle_api_repo_list(self, http_context):
        try:
            http = urllib3.PoolManager()
            return json.loads(http.request('GET', 'http://ajenti.org/plugins/list').data)
        except Exception as e:
            raise EndpointError(e)
