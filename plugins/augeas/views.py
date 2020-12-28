"""
Utility wrapper module for augeas : create endpoints and set the environment to
facilitate the use of augeas.
"""

import json
from jadi import component

from aj.api.http import url, HttpPlugin

from aj.api.endpoint import endpoint, EndpointReturn
from aj.plugins.augeas.api import AugeasEndpoint


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    def __get_augeas_endpoint(self, id):
        """
        Select the right endpoint in the augeas endpoint interface.

        :param id: Augeas endpoint id
        :type id: string
        :return: AugeasEndpoint object
        :rtype: AugeasEndpoint
        """

        for a in AugeasEndpoint.all(self.context):
            if a.id == id:
                return a

    @url(r'/api/augeas/endpoint/get/(?P<id>.+)')
    @endpoint(api=True)
    def handle_api_get(self, http_context, id=None):
        """
        Get file content and informations through augeas endpoint.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param id: Id of augeas endpoint, e.g. hosts
        :type id: string
        :return: Data and file informations
        :rtype: dict
        """

        ep = self.__get_augeas_endpoint(id)
        if not ep:
            raise EndpointReturn(404)

        aug = ep.get_augeas()
        aug.load()
        root_path = ep.get_root_path()

        data = {}

        def __wrap_tree(path):
            r = {
                'name': path.split('/')[-1].split('[')[0],
                'path': path,
                'value': aug.get(path),
                'children': []
            }
            for sp in aug.match(path + '/*'):
                r['children'].append(__wrap_tree(sp))
            return r

        data = __wrap_tree(root_path)
        return data

    @url(r'/api/augeas/endpoint/set/(?P<id>.+)')
    @endpoint(api=True)
    def handle_api_set(self, http_context, id=None):
        """
        Save the data to config file using augeas endpoint.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param id: Augeas endpoint id, e.g. hosts
        :type id: string
        """

        data = json.loads(http_context.body.decode())

        ep = self.__get_augeas_endpoint(id)
        if not ep:
            raise EndpointReturn(404)

        aug = ep.get_augeas()
        aug.load()

        def __apply_tree(e):
            aug.set(e['path'], e['value'])
            for sp in aug.match(e['path'] + '/*'):
                aug.remove(sp)
            for child in e['children']:
                __apply_tree(child)

        __apply_tree(data)
        aug.save()
