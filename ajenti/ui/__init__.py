from ajenti.api import *

import binder
from inflater import Inflater
from element import p, UIElement


class UI (object):
    def __init__(self):
        self.pending_updates = 0
        self.inflater = Inflater(self)

    def create(self, typeid, *args, **kwargs):
        for cls in UIElement.get_classes():
            if cls.typeid == typeid:
                return cls.new(self, *args, **kwargs)
        return UIElement(self, typeid=typeid, *args, **kwargs)

    def inflate(self, layout):
        return self.inflater.inflate(layout)

    def render(self):
        return self.root.render()

    def find(self, id):
        return self.root.find(id)

    def find_uid(self, uid):
        return self.root.find_uid(uid)

    def dispatch_event(self, uid, event, params=None):
        self.find_uid(uid).event(event, params)

    def queue_update(self):
        self.pending_updates += 1

    def get_updates(self):
        updates = [1] * self.pending_updates  # TODO!
        self.pending_updates = 0
        return updates


__all__ = ['UI', 'UIElement', 'p', 'binder']
