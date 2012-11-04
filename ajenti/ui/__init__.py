from ajenti.api import *

import binder
from inflater import Inflater
from element import p, on, UIElement


class UI (object):
    def __init__(self):
        self.inflater = Inflater(self)

    def create(self, typeid, *args, **kwargs):
        cls = self.get_class(typeid)
        inst = cls.new(self, *args, **kwargs)
        inst.typeid = typeid
        return inst

    def get_class(self, typeid):
        for cls in UIElement.get_classes():
            if cls.typeid == typeid:
                return cls
        else:
            return UIElement

    def inflate(self, layout):
        return self.inflater.inflate(layout)

    def render(self):
        return self.root.render()

    def find(self, id):
        return self.root.find(id)

    def find_uid(self, uid):
        return self.root.find_uid(uid)

    def dispatch_event(self, uid, event, params=None):
        self.root.dispatch_event(uid, event, params)

    def has_updates(self):
        return self.root.has_updates()

    def clear_updates(self):
        return self.root.clear_updates()


__all__ = ['UI', 'UIElement', 'p', 'on', 'binder']
