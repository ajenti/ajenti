import json
import logging
import subprocess

import aj
from aj.api import *
from aj.api.http import BaseHttpHandler, url, HttpPlugin, SocketEndpoint
from aj.plugins import PluginManager, DirectoryPluginProvider

from aj.plugins.core.api.endpoint import endpoint


@component(HttpPlugin)
class Handler (HttpPlugin):
    def __init__(self, context):
        pass

    @url('/')
    @endpoint(page=True, auth=False)
    def handle_root(self, http_context):
        return http_context.redirect('/view/')


    @url('/view/.*')
    @endpoint(page=True, auth=False)
    def handle_view(self, http_context):
        if aj.dev:
            cmd = ['./scripts/build-resources']
            if http_context.env.get('HTTP_CACHE_CONTROL', None) == 'no-cache':
                cmd += ['nocache']

            for provider in aj.plugin_providers:
                if type(provider) is DirectoryPluginProvider:
                    logging.debug('Building resources in %s' % provider.path)
                    p = subprocess.Popen(['ajenti-dev-multitool', '--build'], cwd=provider.path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    o, e = p.communicate()
                    if p.returncode != 0:
                        logging.error('Resource compilation failed')
                        logging.error(o + e)
            
        path = PluginManager.get(aj.context).get_content_path('core', 'content/pages/index.html')
        content = open(path).read() % {
            'prefix': http_context.prefix,
            'plugins': json.dumps(
                dict((k, v.title) for k, v in PluginManager.get(aj.context).get_all().iteritems())
            ),
            'version': aj.version,
        }
        http_context.add_header('Content-Type', 'text/html')
        http_context.respond_ok()
        return content
