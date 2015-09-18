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
        for a in AugeasEndpoint.all(self.context):
            if a.id == id:
                return a

    @url(r'/api/augeas/endpoint/get/(?P<id>.+)')
    @endpoint(api=True)
    def handle_api_get(self, http_context, id=None):
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
        data = json.loads(http_context.body)

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
