import gevent
import json
import os
import socket
import subprocess
import traceback

import aj
from aj.api import *
from aj.api.http import BaseHttpHandler, url, HttpPlugin
from aj.plugins import PluginManager
from aj.auth import AuthenticationService, SudoError

from aj.plugins.core.api.endpoint import endpoint
from aj.plugins.core.api.sidebar import Sidebar


@component(HttpPlugin)
class Handler (HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url('/api/core/identity')
    @endpoint(api=True, auth=False)
    def handle_api_identity(self, http_context):
        return {
            'identity': {
                'user': AuthenticationService.get(self.context).get_identity(),
                'effective': os.geteuid(),
            },
            'machine': {
                'name': aj.config.data['name'],
                'hostname': socket.gethostname(),
            },
            'color': aj.config.data['color'],
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
            if auth.check_password(username, password):
                auth.login(username)
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
                auth.check_sudo_password(username, password)
                auth.login(target)
                return {
                    'success': True,
                    'username': target,
                }
            except SudoError as e:
                gevent.sleep(3)
                return {
                    'success': False,
                    'error': e.message,
                }
        elif mode == 'persona':
            assertion = body_data.get('assertion', None)
            audience = body_data.get('audience', None)

            if not assertion or not audience:
                return {
                    'success': False,
                    'error': 'Invalid params',
                }

            try:
                email = auth.check_persona_assertion(assertion, audience)
            except Exception as e:
                traceback.print_exc()
                return {
                    'success': False,
                    'error': 'Could not authenticate with Mozilla Persona: %s' % str(e),
                }

            emails = aj.config.data.get('emails', {})
            if email in emails:
                username = emails[email]
                auth.login(username)
                return {
                    'success': True,
                    'username': username,
                }
            else:
                return {
                    'success': False,
                    'error': 'Unrecognized e-mail',
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
