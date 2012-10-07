import copy

from ajenti.api import *


def p(prop, default=None, bindtypes=[], type=unicode, public=True):
    def decorator(cls):
        prop_obj = UIProperty(prop, value=default, bindtypes=bindtypes, type=type, public=public)
        if not hasattr(cls, '_properties'):
            cls._properties = []
        cls._properties = cls._properties + [prop_obj]

        def get(self):
            return self.properties[prop].get()

        def set(self, value):
            return self.properties[prop].set(value)

        setattr(cls, prop, property(get, set))
        return cls
    return decorator


class UIProperty (object):
    def __init__(self, name, value=None, bindtypes=[], type=unicode, public=True):
        self.dirty = False
        self.name = name
        self.value = value
        self.bindtypes = bindtypes
        self.type = type
        self.public = public

    def clone(self):
        return copy.deepcopy(self)

    def get(self):
        return self.value

    def set(self, value):
        self.dirty = self.value != value
        self.value = value


@p('visible', default=True, type=bool)
@interface
class UIElement (object):
    typeid = None
    __last_id = 0

    @classmethod
    def __generate_id(cls):
        cls.__last_id += 1
        return cls.__last_id

    def __init__(self, ui, typeid=None, **kwargs):
        self.ui = ui

        if typeid is not None:
            self.typeid = typeid

        self.id = None
        self.uid = UIElement.__generate_id()

        if not hasattr(self, '_properties'):
            self._properties = []

        self.children = []

        self.properties = {}
        for prop in self._properties:
            self.properties[prop.name] = prop.clone()
        for key in kwargs:
            self.properties[key].set(kwargs[key])

        self.events = {}
        self.event_args = {}
        self.init()

    def getstate(self):
        return (self.typeid, self.id, self.properties, self.events, self.event_args)

    def setstate(self, s):
        self.typeid, self.id, self.properties, self.events, self.event_args = s

    def clone(self):
        o = copy.copy(self)
        o.uid = UIElement.__generate_id()
        o.setstate(copy.deepcopy(self.getstate()))
        o.children = [c.clone() for c in self.children]
        return o

    def init(self):
        pass

    def nearest(self, predicate):
        r = []
        q = [self]
        while len(q) > 0:
            e = q.pop(0)
            if predicate(e):
                r.append(e)
            q.extend(e.children)
        return r

    def find(self, id):
        r = self.nearest(lambda x: x.id == id)
        return r[0] if len(r) > 0 else None

    def find_uid(self, uid):
        r = self.nearest(lambda x: x.uid == uid)
        return r[0] if len(r) > 0 else None

    def find_type(self, typeid):
        r = self.nearest(lambda x: x.typeid == typeid)
        return r[0] if len(r) > 0 else None

    def contains(self, element):
        return len(self.nearest(lambda x: x == element)) > 0

    def render(self):
        result = {
            'id': self.id,
            'uid': self.uid,
            'typeid': self.typeid,
            'events': self.events.keys(),
            'children': [c.render() for c in self.children],
        }
        for prop in self.properties.values():
            if prop.public:
                result[prop.name] = prop.value
        return result

    def on(self, event, handler, *args):
        self.events[event] = handler
        self.event_args[event] = args

    def publish(self):
        self.ui.queue_update()

    def event(self, event, params=None):
        if event in self.events:
            self.events[event](*self.event_args[event], **(params or {}))

    def empty(self):
        self.children = []

    def append(self, child):
        self.children.append(child)

    def remove(self, child):
        self.children.remove(child)
