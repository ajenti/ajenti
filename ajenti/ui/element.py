import copy
import cPickle

from ajenti.api import *
from ajenti.util import *


@public
def p(prop, default=None, bindtypes=[], type=unicode, public=True, doc=None):
    """
    Creates an UI property inside an :class:`UIElement`::

        @p('title')
        @p('category', default='Other', doc='Section category name')
        @p('active', default=False)
        class SectionPlugin (BasePlugin, UIElement):
            typeid = 'main:section'

    :param default: Default value
    :param bindtypes: List of Python types that can be bound to this property
    :param type: expected Python type for this value
    :param public: whether this property is rendered and sent to client
    :param doc: docstring
    """

    def decorator(cls):
        prop_obj = UIProperty(prop, value=default, bindtypes=bindtypes, type=type, public=public)
        if not hasattr(cls, '_properties'):
            cls._properties = []
        cls._properties = cls._properties + [prop_obj]

        def get(self):
            return self.properties[prop].get()

        def set(self, value):
            return self.properties[prop].set(value)

        _property = property(get, set, None, doc)
        setattr(cls, prop, _property)
        return cls
    return decorator


@public
def on(id, event):
    """
    Sets the decorated method to handle indicated event::

        @plugin
        class Hosts (SectionPlugin):
            def init(self):
                self.append(self.ui.inflate('hosts:main'))
                ...

            @on('save', 'click')
            def save(self):
                self.config.save()

    :param id: element ID
    :param event: event name
    """

    def decorator(fx):
        fx._event_id = id
        fx._event_name = event
        return fx
    return decorator


@public
class UIProperty (object):
    __slots__ = ['dirty', 'name', 'value', 'bindtypes', 'type', 'public']

    def __init__(self, name, value=None, bindtypes=[], type=unicode, public=True):
        self.dirty = False
        self.name = name
        self.value = value
        self.bindtypes = bindtypes
        self.type = type
        self.public = public

    def clone(self):
        return UIProperty(
            self.name,
            self.value,
            self.bindtypes,
            self.type,
            self.public,
        )

    def get(self):
        return self.value

    def set(self, value):
        self.dirty = self.value != value
        self.value = value


@public
@p('visible', default=True, type=bool,
    doc='Visibility of the element')
@p('bind', default=None, type=str,
    doc='Bound property name')
@p('client', default=False, type=True,
    doc='Whether this element\'s events are only processed on client side')
@p('bindtransform', default=None, type=eval, public=False,
    doc='Value transformation function for one-direction bindings')
@p('id', default=None, type=str,
    doc='Element ID')
@p('style', default='normal',
    doc='Additional CSS class')
@plugin
@interface
class UIElement (object):
    """ Base UI element class """

    typeid = None
    """ Unique identifier or element type class, used for XML tag name """

    __last_id = 0

    @classmethod
    def __generate_id(cls):
        cls.__last_id += 1
        return cls.__last_id

    def __init__(self, ui, typeid=None, children=[], **kwargs):
        self.ui = ui

        if typeid is not None:
            self.typeid = typeid

        #: Generated unique identifier (UID)
        self.uid = UIElement.__generate_id()

        if not hasattr(self, '_properties'):
            self._properties = []

        self.parent = None

        self.children = []
        for c in children:
            self.append(c)
        self.children_changed = False
        self.invalidated = False

        # Copy properties from the class
        self.properties = {}
        for prop in self._properties:
            self.properties[prop.name] = prop.clone()
        for key in kwargs:
            self.properties[key].set(kwargs[key])

        self.events = {}
        self.event_args = {}

    def __str__(self):
        return '<%s @ %s>' % (self.typeid, id(self))

    def clone(self):
        """
        :returns: a deep copy of the element and its children. Property values are shallow copies.
        """
        o = copy.copy(self)
        o.uid = UIElement.__generate_id()

        o.events = self.events.copy()
        o.event_args = self.event_args.copy()
        o.properties = {}
        for p in self.properties:
            o.properties[p] = self.properties[p].clone()

        o.children = []
        for c in self.children:
            o.append(c.clone())
        return o

    def init(self):
        pass

    def nearest(self, predicate):
        """
        Returns the nearest child which matches an arbitrary predicate lambda

        :param predicate: ``lambda element: bool``
        """
        r = []
        q = [self]
        while len(q) > 0:
            e = q.pop(0)
            if predicate(e):
                r.append(e)
            q.extend(e.children)
        return r

    def find(self, id):
        """
        :returns: the nearest child with given ID or ``None``
        """
        r = self.nearest(lambda x: x.id == id)
        return r[0] if len(r) > 0 else None

    def find_uid(self, uid):
        """
        :returns: the nearest child with given UID or ``None``
        """
        r = self.nearest(lambda x: x.uid == uid)
        return r[0] if len(r) > 0 else None

    def find_type(self, typeid):
        """
        :returns: the nearest child with given type ID or ``None``
        """
        r = self.nearest(lambda x: x.typeid == typeid)
        return r[0] if len(r) > 0 else None

    def contains(self, element):
        """
        Checks if the ``element`` is in the subtree of ``self``
        """
        return len(self.nearest(lambda x: x == element)) > 0

    def path_to(self, element):
        """
        :returns: a list of elements forming a path from ``self`` to ``element``
        """
        r = []
        while element != self:
            r.insert(0, element)
            element = element.parent
        return r

    def render(self):
        """
        Renders this element and its subtree to JSON
        """
        result = {
            'id': self.id,
            'uid': self.uid,
            'typeid': self.typeid,
            'events': self.events.keys(),
            'children': [c.render() for c in self.children if self.visible],
        }
        for prop in self.properties.values():
            if prop.public:
                result[prop.name] = prop.value
        return result

    def on(self, event, handler, *args):
        """
        Binds event with ID ``event`` to ``handler``. ``*args`` will be passed to the ``handler``.
        """
        self.events[event] = handler
        self.event_args[event] = args

    def has_updates(self):
        """
        Checks for pending UI updates
        """
        if self.children_changed or self.invalidated:
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
        """
        Marks all pending updates as processed
        """
        self.children_changed = False
        self.invalidated = False
        for property in self.properties.values():
            property.dirty = False
        if self.visible:
            for child in self.children:
                if child.has_updates():
                    child.clear_updates()

    def invalidate(self):
        self.invalidated = True

    def broadcast(self, method, *args, **kwargs):
        """
        Calls ``method`` on every member of the subtree
        """
        if hasattr(self, method):
            getattr(self, method)(*args, **kwargs)

        for child in self.children:
            child.broadcast(method, *args, **kwargs)

    def dispatch_event(self, uid, event, params=None):
        """
        Dispatches an event to an element with given UID
        """
        if self.uid == uid:
            self.event(event, params)
            return True
        else:
            for child in self.children:
                if child.dispatch_event(uid, event, params):
                    for k in dir(self):
                        v = getattr(self, k)
                        if hasattr(v, '_event_id'):
                            element = self.find(v._event_id)
                            if element and element.uid == uid and v._event_name == event:
                                getattr(self, k)(**(params or {}))
                    return True

    def event(self, event, params=None):
        """
        Invokes handler for ``event`` on this element with given ``**params``
        """
        if hasattr(self, 'on_%s' % event):
            getattr(self, 'on_%s' % event)(**(params or {}))
        if event in self.events:
            self.events[event](*self.event_args[event], **(params or {}))

    def reverse_event(self, event, params=None):
        """
        Raises the event on this element by feeding it to the UI root (so that ``@on`` methods in ancestors will work).
        """
        self.ui.dispatch_event(self.uid, event, params)

    def empty(self):
        """
        Detaches all child elements
        """
        self.children = []
        self.children_changed = True

    def append(self, child):
        """
        Appends a ``child``
        """
        if child in self.children:
            return
        self.children.append(child)
        child.parent = self
        self.children_changed = True

    def remove(self, child):
        """
        Detaches the ``child``
        """
        self.children.remove(child)
        child.parent = None
        self.children_changed = True
