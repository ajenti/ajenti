import gevent
import json
import logging
import subprocess
import os
import pwd
from jadi import component

import aj
from aj.api.http import url, HttpPlugin
from aj.plugins import PluginManager, DirectoryPluginProvider

from aj.api.endpoint import endpoint


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url('/')
    @endpoint(page=True, auth=False)
    def handle_root(self, http_context):
        if self.context.identity:
            return http_context.redirect('/view/')
        else:
            return http_context.redirect('/view/login/normal')

    @url('/view/.*')
    @endpoint(page=True, auth=False)
    def handle_view(self, http_context):
        if aj.dev:
            restricted_user = aj.config.data['restricted_user']
            if os.getuid() != pwd.getpwnam(restricted_user).pw_uid:
                rebuild_all = http_context.env.get('HTTP_CACHE_CONTROL', None) == 'no-cache'

                for provider in aj.plugin_providers:
                    if isinstance(provider, DirectoryPluginProvider):
                        logging.debug('Building resources in %s', provider.path)
                        if rebuild_all:
                            cmd = ['ajenti-dev-multitool', '--rebuild']
                        else:
                            cmd = ['ajenti-dev-multitool', '--build']
                        p = subprocess.Popen(
                            cmd,
                            cwd=provider.path,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
                        )
                        o, e = p.communicate()
                        if p.returncode != 0:
                            logging.error('Resource compilation failed')
                            logging.error(o+e)
            else:
                logging.warning("Cannot build resources as restricted user %s", restricted_user)

        manager = PluginManager.get(aj.context)
        path = manager.get_content_path('core', 'content/pages/index.html')

        conf_data = aj.config.data.copy()
        for user in list(conf_data["auth"]["users"]):
            try:
                del conf_data["auth"]["users"][user]["password"]
            except:
                pass
   
        content = open(path).read() % {
            'prefix': http_context.prefix,
            'plugins': json.dumps(
                {manager[n]['info']['name']:manager[n]['info']['title'] for n in manager}
            ),
            'config': json.dumps(conf_data),
            'version': str(aj.version),
            'platform': aj.platform,
            'platformUnmapped': aj.platform_unmapped,
            'bootstrapColor': aj.config.data.get('color', None),
        }
        http_context.add_header('Content-Type', 'text/html')
        http_context.respond_ok()
        return content
