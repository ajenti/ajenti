import gevent
import simplejson as json
import os
import socket
import logging
from jadi import component
from time import time

import aj
from aj.api.http import get, post, HttpPlugin
from aj.auth import AuthenticationService, SudoError
from aj.plugins import PluginManager

from aj.api.endpoint import endpoint, EndpointError
from aj.plugins.core.api.sidebar import Sidebar
from aj.plugins.core.api.navbox import Navbox


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @get('/api/core/identity')
    @endpoint(api=True, auth=False)
    def handle_api_identity(self, http_context):
        """
        Collect user and server informations from authentication service and
        ajenti config file.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: User and server informations and profil.
        :rtype: dict
        """

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

    @get('/api/core/web-manifest')
    @endpoint(api=True, auth=False)
    def handle_api_web_manifest(self, http_context):
        """
        Prepare a web-manifest for the metadata of the frontend.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Manifest data
        :rtype: dict
        """

        return {
            'short_name': aj.config.data['name'],
            'name': f'{aj.config.data["name"]} ({socket.gethostname()})',
            'start_url': f'{http_context.prefix}/#app',
            'display': 'standalone',
            'icons': [
                {
                    'src': f'{http_context.prefix}/resources/core/resources/images/icon.png',
                    'sizes': '1024x1024',
                    'type': 'image/png',
                }
            ]
        }

    @post('/api/core/auth')
    @endpoint(api=True, auth=False)
    def handle_api_auth(self, http_context):
        """
        Test user authentication to login or to elevate privileges.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Success status and username
        :rtype: dict
        """

        body_data = json.loads(http_context.body.decode())
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

            # Log failed login for e.g. fail2ban
            remote_addr = http_context.env.get('REMOTE_ADDR', None)
            if len(aj.config.data['trusted_proxies']) > 0:
                if remote_addr in aj.config.data['trusted_proxies']:
                    ip = http_context.env.get('HTTP_X_FORWARDED_FOR', '').split(',')[0]
            else:
                ip = remote_addr
            logging.warning(f"Failed login from {username} at IP : {ip}")

            gevent.sleep(3)
            return {
                'success': False,
                'error': None,
            }

        elif mode == 'sudo':
            target = 'root'
            try:
                if auth.check_sudo_password(username, password):
                    self.context.worker.terminate()
                    auth.prepare_session_redirect(http_context, target, None)
                    return {
                        'success': True,
                        'username': target,
                    }

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

    @post('/api/core/logout')
    @endpoint(api=True, auth=False)
    def handle_api_logout(self, http_context):
        """
        Logout by closing associated worker.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        AuthenticationService.get(self.context).get_provider().signout()
        self.context.worker.terminate()

    @get('/api/core/sidebar')
    @endpoint(api=True)
    def handle_api_sidebar(self, http_context):
        """
        Build sidebar.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All permitted sidebar items
        :rtype: dict
        """

        return {
            'sidebar': Sidebar.get(self.context).build(),
        }

    @get('/api/core/navbox/(?P<query>.+)')
    @endpoint(api=True)
    def handle_api_navbox(self, http_context, query=None):
        """
        Connector to query some search in the sidebar items through navbox.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param query: Search query
        :type query: string
        :return: List of sidebar items, one item per dict
        :rtype: list of dict
        """

        return Navbox.get(self.context).search(query)

    @post('/api/core/restart-master')
    @endpoint(api=True)
    def handle_api_restart_master(self, http_context):
        """
        Send restart signal to the root process.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        self.context.worker.restart_master()

    @get('/api/core/languages')
    @endpoint(api=True)
    def handle_api_languages(self, http_context):
        """
        List all availables languages.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of languages
        :rtype: list
        """

        mgr = PluginManager.get(aj.context)
        languages = set()
        for id in mgr:
            locale_dir = mgr.get_content_path(id, 'locale')
            if os.path.isdir(locale_dir):
                for lang in os.listdir(locale_dir):
                    if lang != 'app.pot':
                        languages.add(lang)

        return sorted(list(languages))

    @get('/api/core/session-time')
    @endpoint(api=True)
    def handle_api_sessiontime(self, http_context):
        """
        Update user auto logout time. It occurs when the user did some action,
        in order to extend the session time if the user is active.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Remaining time
        :rtype: integer
        """

        if aj.dev_autologin:
            return 86400

        self.context.worker.update_sessionlist()
        # Wait until the new values propagate
        gevent.sleep(0.01)
        session_max_time = aj.config.data['session_max_time'] if aj.config.data['session_max_time'] else 3600
        timestamp = 0
        if self.context.session.key in aj.sessions.keys():
            timestamp = aj.sessions[self.context.session.key]['timestamp']
        return int(timestamp + session_max_time - time())


    @post('/api/core/check_password_complexity')
    @endpoint(api=True, auth=False)
    def handle_api_check_password_complexity(self, http_context):
        """
        Check the password complexity requirements from the auth provider before saving a new password for the password reset functionality.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Error if test failed
        :rtype: basestring
        """

        password = http_context.json_body()['password']
        return AuthenticationService.get(self.context).get_provider().check_password_complexity(password)
