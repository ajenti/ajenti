import json
import logging
import subprocess
import os
import pwd
from jadi import component

import aj
from aj.api.http import get, post, HttpPlugin
from aj.plugins import PluginManager, DirectoryPluginProvider
from aj.auth import AuthenticationService
from aj.api.endpoint import endpoint


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    get('/')
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

    @get('/view.*')
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

        manager = PluginManager.get(aj.context)
        # Path eventually need to be customizable
        path = manager.get_content_path('core', 'resources/build/index.html')
        with open(path, 'r') as index:
            content = index.read()
        http_context.add_header('Content-Type', 'text/html')
        http_context.respond_ok()
        return content
