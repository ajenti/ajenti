from ajenti.api import *

import binder
from inflater import Inflater
from element import p, on, UIElement


@plugin
class UI (BasePlugin):
    """
    The root UI object, one per session
    """

    def __init__(self):
        self.inflater = Inflater(self)

    def create(self, typeid, *args, **kwargs):
        """
        Creates an element by its type ID.
        """
        cls = self.get_class(typeid)
        inst = cls.new(self, context=self.context, *args, **kwargs)
        inst.typeid = typeid
        return inst

    def get_class(self, typeid):
        """
        :returns: element class by element type ID
        """
        for cls in UIElement.get_classes():
            if cls.typeid == typeid:
                return cls
        else:
            return UIElement

    def inflate(self, layout):
        """
        :returns: an inflated element tree of the given layout XML name
        """
        return self.inflater.inflate(layout)

    def render(self):
        """
        Renders the UI into JSON
        """
        return self.root.render()

    def find(self, id):
        """
        :returns: nearest element with given ID
        """
        return self.root.find(id)

    def find_uid(self, uid):
        """
        :returns: nearest element with given unique ID
        """
        return self.root.find_uid(uid)

    def dispatch_event(self, uid, event, params=None):
        """
        Dispatches an event to an element with given UID
        """
        self.root.dispatch_event(uid, event, params)

    def has_updates(self):
        """
        Checks for pending UI updates
        """
        return self.root.has_updates()

    def clear_updates(self):
        """
        Marks all pending updates as processed
        """
        return self.root.clear_updates()


__all__ = ['UI', 'UIElement', 'p', 'on', 'binder']
