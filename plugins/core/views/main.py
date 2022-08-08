import json
import logging
import subprocess
import os
import pwd
from jadi import component

import aj
from aj.api.http import get, HttpPlugin
from aj.plugins import PluginManager, DirectoryPluginProvider
from aj.auth import AuthenticationService
from aj.api.endpoint import endpoint


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @get('/')
    @endpoint(page=True, auth=False)
    def handle_root(self, http_context):
        """
        Root url and redirect to login if user has no session.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Empty string
        :rtype: string
        """

        if self.context.identity:
            return http_context.redirect('/view/')
        return http_context.redirect('/view/login/normal')

    @get('/view/.*')
    @endpoint(page=True, auth=False)
    def handle_view(self, http_context):
        """
        Catch all for all not handled url. Generate an appropriate page and reload all
        extern resources if ajenti is used in dev mode.
        This function is also called when a page is refreshed through F5.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Page content
        :rtype: string
        """

        if aj.dev:
            if os.getuid() == 0:
                rebuild_all = http_context.env.get('HTTP_CACHE_CONTROL', None) == 'no-cache'

                for provider in aj.plugin_providers:
                    if isinstance(provider, DirectoryPluginProvider):
                        logging.debug(f'Building resources in {provider.path}')
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
                            logging.error((o+e).decode('utf-8'))
            else:
                logging.warning("Cannot build resources without root permissions.")

        manager = PluginManager.get(aj.context)

        try:
            path = manager.get_content_path(
                aj.config.data['view']['plugin'],
                aj.config.data['view']['filepath'],
            )
        except KeyError:
            logging.error(
                f"Could not open template view : plugin {aj.config.data['view']['plugin']} not found"
            )
            path = manager.get_content_path('core', 'content/pages/index.html')
            logging.info(f'Using default view at {path}')

        if not os.path.isfile(path):
            logging.error(f'Could not open template view: {path} not found')
            path = manager.get_content_path('core', 'content/pages/index.html')
            logging.info(f'Using default view at {path}')

        with open(path, 'r') as view:
            content = view.read() % {
                'prefix': http_context.prefix,
                'plugins': json.dumps(
                    {manager[n]['info']['name']:manager[n]['info']['title'] for n in manager}
                ),
                'config': json.dumps(aj.config.get_non_sensitive_data()),
                'version': str(aj.version),
                'platform': aj.platform,
                'platformUnmapped': aj.platform_unmapped,
                'devMode': aj.dev,
                'pwReset': getattr(AuthenticationService.get(self.context).get_provider(), 'pw_reset', False),
                'bootstrapColor': aj.config.data.get('color', None),
            }

        http_context.add_header('Content-Type', 'text/html')
        http_context.respond_ok()
        return content
