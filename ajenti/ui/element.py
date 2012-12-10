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


def on(id, event):
    def decorator(fx):
        fx._event_id = id
        fx._event_name = event
        return fx
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
@p('bind', default=None, type=str)
@p('client', default=False, type=True)
@p('bindtransform', default=lambda x: x, type=eval, public=False)
@p('id', default=None, type=str)
@plugin
@interface
class UIElement (object):
    typeid = None
    __last_id = 0

    @classmethod
    def __generate_id(cls):
        cls.__last_id += 1
        return cls.__last_id

    def __init__(self, ui, typeid=None, children=[], **kwargs):
        self.ui = ui

        if typeid is not None:
            self.typeid = typeid

        self.uid = UIElement.__generate_id()

        if not hasattr(self, '_properties'):
            self._properties = []

        self.children = []
        self.children.extend(children)
        self.children_changed = False

        self.properties = {}
        for prop in self._properties:
            self.properties[prop.name] = prop.clone()
        for key in kwargs:
            self.properties[key].set(kwargs[key])

        self.events = {}
        self.event_args = {}

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

    def has_updates(self):
        if self.children_changed:
            return True
        for property in self.properties.values():
            if property.dirty:
                return True
        if self.visible:
            for child in self.children:
                if child.has_updates():
                    return True
        return False

    def clear_updates(self):
        self.children_changed = False
        for property in self.properties.values():
            property.dirty = False
        if self.visible:
            for child in self.children:
                if child.has_updates():
                    child.clear_updates()

    def broadcast(self, method, *args, **kwargs):
        if hasattr(self, method):
            getattr(self, method)(*args, **kwargs)

        for child in self.children:
            child.broadcast(method, *args, **kwargs)

    def dispatch_event(self, uid, event, params=None):
        if self.uid == uid:
            self.event(event, params)
            return True
        else:
            for child in self.children:
                if child.dispatch_event(uid, event, params):
                    for k, v in self.__class__.__dict__.iteritems():
                        if hasattr(v, '_event_id'):
                            if self.find(v._event_id).uid == uid and v._event_name == event:
                                getattr(self, k)(**(params or {}))
                    return True

    def event(self, event, params=None):
        if hasattr(self, 'on_%s' % event):
            getattr(self, 'on_%s' % event)(**(params or {}))
        if event in self.events:
            self.events[event](*self.event_args[event], **(params or {}))

    def reverse_event(self, event, params=None):
        self.ui.dispatch_event(self.uid, event, params)

    def empty(self):
        self.children = []
        self.children_changed = True

    def append(self, child):
        self.children.append(child)
        self.children_changed = True

    def remove(self, child):
        self.children.remove(child)
        self.children_changed = True
