import gevent
import json
import os
import socket
import traceback
from jadi import component

import aj
from aj.api.http import url, HttpPlugin
from aj.auth import AuthenticationService, SudoError
from aj.plugins import PluginManager

from aj.api.endpoint import endpoint
from aj.plugins.core.api.sidebar import Sidebar
from aj.plugins.core.api.navbox import Navbox


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url('/api/core/identity')
    @endpoint(api=True, auth=False)
    def handle_api_identity(self, http_context):
        return {
            'identity': {
                'user': AuthenticationService.get(self.context).get_identity(),
                'uid': os.getuid(),
                'effective': os.geteuid(),
                'elevation_allowed': aj.config.data['auth'].get('allow_sudo', False),
                'profile': AuthenticationService.get(self.context).get_provider().get_profile(
                    AuthenticationService.get(self.context).get_identity()
                ),
            },
            'machine': {
                'name': aj.config.data['name'],
                'hostname': socket.gethostname(),
            },
            'color': aj.config.data.get('color', None),
        }

    @url('/api/core/web-manifest')
    @endpoint(api=True, auth=False)
    def handle_api_web_manifest(self, http_context):
        return {
            'short_name': aj.config.data['name'],
            'name': '%s (%s)' % (aj.config.data['name'], socket.gethostname()),
            'start_url': '%s/#app' % http_context.prefix,
            'display': 'standalone',
            'icons': [
                {
                    'src': '%s/resources/core/resources/images/icon.png' % http_context.prefix,
                    'sizes': '1024x1024',
                    'type': 'image/png',
                }
            ]
        }

    @url('/api/core/auth')
    @endpoint(api=True, auth=False)
    def handle_api_auth(self, http_context):
        body_data = json.loads(http_context.body)
        mode = body_data['mode']
        username = body_data.get('username', None)
        password = body_data.get('password', None)

        auth = AuthenticationService.get(self.context)

        if mode == 'normal':
            auth_info = auth.check_password(username, password)
            if auth_info:
                auth.prepare_session_redirect(http_context, username, auth_info)
                return {
                    'success': True,
                    'username': username,
                }
            else:
                gevent.sleep(3)
                return {
                    'success': False,
                    'error': None,
                }
        elif mode == 'sudo':
            target = 'root'
            try:
                if auth.check_sudo_password(username, password):
                    auth.prepare_session_redirect(http_context, target, None)
                    return {
                        'success': True,
                        'username': target,
                    }
                else:
                    gevent.sleep(3)
                    return {
                        'success': False,
                        'error': _('Authorization failed'),
                    }
            except SudoError as e:
                gevent.sleep(3)
                return {
                    'success': False,
                    'error': e.message,
                }
        return {
            'success': False,
            'error': 'Invalid mode',
        }

    @url('/api/core/logout')
    @endpoint(api=True, auth=False)
    def handle_api_logout(self, http_context):
        self.context.worker.terminate()

    @url('/api/core/sidebar')
    @endpoint(api=True)
    def handle_api_sidebar(self, http_context):
        return {
            'sidebar': Sidebar.get(self.context).build(),
        }

    @url('/api/core/navbox/(?P<query>.+)')
    @endpoint(api=True)
    def handle_api_navbox(self, http_context, query=None):
        return Navbox.get(self.context).search(query)

    @url('/api/core/restart-master')
    @endpoint(api=True)
    def handle_api_restart_master(self, http_context):
        self.context.worker.restart_master()

    @url('/api/core/languages')
    @endpoint(api=True)
    def handle_api_languages(self, http_context):
        mgr = PluginManager.get(aj.context)
        languages = set()
        for id in mgr:
            locale_dir = mgr.get_content_path(id, 'locale')
            if os.path.isdir(locale_dir):
                for lang in os.listdir(locale_dir):
                    if lang != 'app.pot':
                        languages.add(lang)

        return sorted(list(languages))
