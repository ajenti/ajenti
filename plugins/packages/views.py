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
        self.managers = dict((x.id, x) for x in PackageManager.all(self.context))

    def __package_to_json(self, package):
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
        return [
            {
                'id': mgr.id,
                'name': mgr.name,
            } for mgr in self.managers.values()
        ]

    @url(r'/api/packages/list/(?P<manager_id>\w+)')
    @endpoint(api=True)
    def handle_api_list(self, http_context, manager_id=None):
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
        return self.__package_to_json(self.managers[manager_id].get_package(package_id))

    @url(r'/api/packages/apply/(?P<manager_id>\w+)')
    @authorize('packages:install')
    @endpoint(api=True)
    def handle_api_apply(self, http_context, manager_id=None):
        mgr = self.managers[manager_id]
        selection = json.loads(http_context.body)
        cmd = mgr.get_apply_cmd(selection)
        return {
            'terminalCommand': cmd,
        }
