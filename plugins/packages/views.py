"""
Module to list, install and remove package on the current system.
"""

import json

from jadi import component
from aj.api.http import url, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint
from aj.plugins.packages.api import PackageManager


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context
        self.managers = {x.id:x for x in PackageManager.all(self.context, ignore_exceptions=True)}

    def __package_to_json(self, package):
        """
        Convert package object into dict for convenience in angular.

        :param package: Package object
        :type package: Package object
        :return: Dict of informations from the package
        :rtype: dict
        """

        return {
            'id': package.id,
            'name': package.name,
            'version': package.version,
            'description': package.description,
            'managerId': package.manager.id,
            'isInstalled': package.is_installed,
            'isUpgradeable': package.is_upgradeable,
            'installedVersion': package.installed_version,
        }

    @url(r'/api/packages/managers')
    @endpoint(api=True)
    def handle_api_managers(self, http_context):
        """
        List all availables managers.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of manager, one per dict
        :rtype: list of dict
        """

        return [
            {
                'id': mgr.id,
                'name': mgr.name,
            } for mgr in self.managers.values()
        ]

    @url(r'/api/packages/list/(?P<manager_id>\w+)')
    @endpoint(api=True)
    def handle_api_list(self, http_context, manager_id=None):
        """
        Filter installed packages names with query string.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param manager_id: Name of the manager, e.g. apt
        :type manager_id: string
        :return: List of packages informations, one per dict
        :rtype: list of dict
        """

        query = http_context.query['query']
        if len(query) < 3:
            raise Exception('Query too short')
        query = query.lower().strip()
        return [
            self.__package_to_json(package)
            for package in self.managers[manager_id].list(query=query)
            if query in package.id or query in package.name
        ]

    @url(r'/api/packages/get/(?P<manager_id>\w+)/(?P<package_id>\w+)')
    @endpoint(api=True)
    def handle_api_get(self, http_context, manager_id=None, package_id=None):
        """
        Get informations for one specific package, in one specific manager.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param manager_id: Name of the manager, e.g. apt
        :type manager_id: string
        :param package_id: Name of the package, e.g. cups
        :type package_id: string
        :return: Package informations
        :rtype: dict
        """

        return self.__package_to_json(self.managers[manager_id].get_package(package_id))

    @url(r'/api/packages/apply/(?P<manager_id>\w+)')
    @authorize('packages:install')
    @endpoint(api=True)
    def handle_api_apply(self, http_context, manager_id=None):
        """
        Prepare command to apply in order to launch it i na terminal.
        Commands may be install, upgrade, remove.
        Packages and commands are given in post body.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param manager_id: Name of the manager, e.g. apt
        :type manager_id: strign
        :return: Terminal command
        :rtype: dict
        """

        mgr = self.managers[manager_id]
        selection = json.loads(http_context.body.decode())
        cmd = mgr.get_apply_cmd(selection)
        return {
            'terminalCommand': cmd,
        }
