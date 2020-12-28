"""
Module to get network interfaces informations from the system.
"""

import json

from jadi import component
from aj.api.http import url, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint
from aj.plugins.network.api import NetworkManager


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context
        self.manager = NetworkManager.any(self.context)

    @url(r'/api/network/config/get')
    @endpoint(api=True)
    def handle_api_config_get(self, http_context):
        """
        Connector to get network interface configuration.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List iface informations, one iface per dict
        :rtype: list of dict
        """

        return self.manager.get_config()

    @url(r'/api/network/config/set')
    @authorize('network:configure')
    @endpoint(api=True)
    def handle_api_config_set(self, http_context):
        """
        Connector to set network interface configuration.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Nothing
        :rtype: None
        """

        return self.manager.set_config(json.loads(http_context.body.decode()))

    @url(r'/api/network/state/(?P<iface>.+)')
    @endpoint(api=True)
    def handle_api_state(self, http_context, iface=None):
        """
        Connector to get iface status.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param iface: Network interface, e.g. eth0
        :type iface: string
        :return: IP and status
        :rtype: dict
        """

        return self.manager.get_state(iface)

    @url(r'/api/network/up/(?P<iface>.+)')
    @authorize('network:updown')
    @endpoint(api=True)
    def handle_api_up(self, http_context, iface=None):
        """
        Connector to bring an iface up.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param iface: Network interface, e.g. eth0
        :type iface: string
        :return: Nothing
        :rtype: None
        """

        return self.manager.up(iface)

    @url(r'/api/network/down/(?P<iface>.+)')
    @authorize('network:updown')
    @endpoint(api=True)
    def handle_api_down(self, http_context, iface=None):
        """
        Connector to bring an iface down.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param iface: Network interface, e.g. eth0
        :type iface: string
        :return: Nothing
        :rtype: None
        """

        return self.manager.down(iface)

    @url(r'/api/network/downup/(?P<iface>.+)')
    @authorize('network:updown')
    @endpoint(api=True)
    def handle_api_downup(self, http_context, iface=None):
        """
        Connector to restart an iface.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param iface: Network interface, e.g. eth0
        :type iface: string
        :return: Nothing
        :rtype: None
        """

        self.manager.down(iface)
        self.manager.up(iface)

    @url(r'/api/network/hostname/get')
    @endpoint(api=True)
    def handle_api_hostname_get(self, http_context):
        """
        Connector to get hostname.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Hostname
        :rtype: string
        """

        return self.manager.get_hostname()

    @url(r'/api/network/hostname/set')
    @authorize('network:configure')
    @endpoint(api=True)
    def handle_api_hostname_set(self, http_context):
        """
        Connector to set hostname.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        self.manager.set_hostname(http_context.body.decode())
