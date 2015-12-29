from jadi import interface, service
from aj.auth import authorize, SecurityError


@interface
class SidebarItemProvider(object):
    """
    Interface for providing sidebar items.
    """
    def __init__(self, context):
        pass

    def provide(self):
        """
        Should return a list of sidebar items, each in the following format::

            {
                'id': 'optional-id',
                'attach': 'category:general', # id of the attachment point or None for top level
                'name': 'Dashboard',
                'icon': 'bar-chart',
                'url': '/view/dashboard',
                'children': [
                    ...
                ]
            }


        :returns: list(dict)
        """
        return []


@service
class Sidebar(object):
    def __init__(self, context):
        self.context = context

    def build(self):
        """
        Returns a complete tree of sidebar items.

        :returns: dict
        """
        sidebar = {
            'id': None,
            'children': [],
        }

        def find_id(_id, e=sidebar):
            if 'id' in e and e['id'] == _id:
                return e
            for c in e.get('children', []):
                f = find_id(_id, e=c)
                if f:
                    return f

        for provider in SidebarItemProvider.all(self.context):
            for item in provider.provide():
                if 'url' in item:
                    try:
                        authorize('sidebar:view:%s' % item['url']).check()
                    except SecurityError:
                        continue

                attach_to = find_id(item['attach'])
                if not attach_to:
                    raise Exception('Attachment point not found: %s' % item['attach'])
                attach_to['children'].append(item)

        return sidebar
