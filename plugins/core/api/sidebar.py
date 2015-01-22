from aj.api import *


@interface
class SidebarItemProvider (object):
    def __init__(self, context):
        pass

    def provide(self):
        return []


@service
class Sidebar (object):
    def __init__(self, context):
        self.context = context

    def build(self):
        sidebar = {
            'id': None,
            'children': [],
        }
        id_map = {
            None: sidebar
        }

        def find_id(id, e=sidebar):
            if 'id' in e and e['id'] == id:
                return e
            for c in e['children']:
                f = find_id(id, e=c)
                if f:
                    return f

        for provider in SidebarItemProvider.all(self.context):
            for item in provider.provide():
                attach_to = find_id(item['attach'])
                if not attach_to:
                    raise Exception('Attachment point not found: %s' % item['attach'])
                attach_to['children'].append(item)

        return sidebar
