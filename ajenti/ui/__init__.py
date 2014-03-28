from ajenti.api import *

import binder
from inflater import Inflater
from element import p, on, UIElement


@plugin
class UI (BasePlugin):
    """
    The root UI object, one per session
    """

    def init(self):
        self.inflater = Inflater.get()

    def create(self, typeid, *args, **kwargs):
        """
        Creates an element by its type ID.

        :param typeid: type ID
        :type typeid: str
        """
        return self.inflater.create_element(self, typeid, *args, **kwargs)

    def inflate(self, layout):
        """
        :param layout: layout spec: "<plugin id>:<layout file name without extension>"
        :type  layout: str
        :returns: an inflated element tree of the given layout XML name
        :rtype: UIElement
        """
        return self.inflater.inflate(self, layout)

    def render(self):
        """
        Renders the UI into JSON

        :rtype: dict
        """
        return self.root.render()

    def find(self, id):
        """
        :param id: element ID
        :type  id: str
        :returns: nearest element with given ID
        :rtype: UIElement, None
        """
        return self.root.find(id)

    def find_uid(self, uid):
        """
        :param uid: element UID
        :type  uid: int
        :returns: nearest element with given unique ID
        :rtype: UIElement, None
        """
        return self.root.find_uid(uid)

    def dispatch_event(self, uid, event, params=None):
        """
        Dispatches an event to an element with given UID

        :param uid: element UID
        :type  uid: int
        :param event: event name
        :type  event: str
        :param params: event arguments
        :type  params: dict, None
        """
        self.root.dispatch_event(uid, event, params)

    def has_updates(self):
        """
        Checks for pending UI updates

        :rtype: bool
        """
        return self.root.has_updates()

    def clear_updates(self):
        """
        Marks all pending updates as processed
        """
        return self.root.clear_updates()


__all__ = ['UI', 'UIElement', 'p', 'on', 'binder']
