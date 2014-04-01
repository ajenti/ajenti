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
    :type  default: object
    :param bindtypes: List of Python types that can be bound to this property
    :type  bindtypes: list
    :param type: expected Python type for this value
    :type  type: object
    :param public: whether this property is rendered and sent to client
    :type  public: bool
    :param doc: docstring
    :type  doc: str, None
    :rtype: function
    """

    def decorator(cls):
        prop_obj = UIProperty(prop, default=default, bindtypes=bindtypes, type=type, public=public)
        if not hasattr(cls, '_properties'):
            cls._properties = {}
        cls._properties = cls._properties.copy()
        cls._properties[prop] = prop_obj

        def get(self):
            return self.properties[prop]

        def set(self, value):
            self.properties_dirty[prop] |= self.properties[prop] != value
            self.properties[prop] = value

        _property = property(get, set, None, doc)
        if not hasattr(cls, prop):
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
    :type  id: str
    :param event: event name
    :type  event: str
    :rtype: function
    """

    def decorator(fx):
        fx._event_id = id
        fx._event_name = event
        return fx
    return decorator


@public
class UIProperty (object):
    __slots__ = ['name', 'default', 'bindtypes', 'type', 'public']

    def __init__(self, name, default=None, bindtypes=[], type=unicode, public=True):
        self.name = name
        self.default = default
        self.bindtypes = bindtypes
        self.type = type
        self.public = public

    def clone(self):
        return UIProperty(
            self.name,
            self.default,
            self.bindtypes,
            self.type,
            self.public,
        )


@public
@p('visible', default=True, type=bool,
    doc='Visibility of the element')
@p('bind', default=None, type=str, public=False,
    doc='Bound property name')
@p('client', default=False, type=True,
    doc='Whether this element\'s events are only processed on client side')
@p('bindtransform', default=None, type=eval, public=False,
    doc='Value transformation function for one-direction bindings')
@p('id', default=None, type=str, public=False,
    doc='Element ID')
@p('style', default='normal',
    doc='Additional CSS class')
@interface
@notrack
class UIElement (object):
    """ Base UI element class """

    typeid = None
    """ Unique identifier or element type class, used for XML tag name """

    __last_id = 0

    @classmethod
    def __generate_id(cls):
        cls.__last_id += 1
        return cls.__last_id

    def _prepare(self):
        #: Generated unique identifier (UID)
        self.uid = UIElement.__generate_id()
        if not hasattr(self, '_properties'):
            self._properties = []
        self.parent = None
        self.children = []
        self.children_changed = False
        self.invalidated = False
        self.events = {}
        self.event_args = {}
        self.context = None

    def __init__(self, ui, typeid=None, children=[], **kwargs):
        """
        :param ui: UI
        :type  ui: :class:`ajenti.ui.UI`
        :param typeid: type ID
        :type  typeid: str
        :param children:
        :type  children: list
        """
        self.ui = ui
        self._prepare()

        if typeid is not None:
            self.typeid = typeid

        for c in children:
            self.append(c)

        # Copy properties from the class
        self.properties = {}
        self.properties_dirty = {}
        for prop in self._properties.values():
            self.properties[prop.name] = prop.default
            self.properties_dirty[prop.name] = False
        for key in kwargs:
            self.properties[key] = kwargs[key]

    def __str__(self):
        return '<%s # %s>' % (self.typeid, self.uid)

    @property
    def property_definitions(self):
        return self.__class__._properties

    def clone(self, set_ui=None, set_context=None):
        """
        :returns: a deep copy of the element and its children. Property values are shallow copies.
        :rtype: :class:`UIElement`
        """
        o = self.__class__.__new__(self.__class__)
        o._prepare()
        o.ui, o.typeid, o.context = (set_ui or self.ui), self.typeid, (set_context or self.context)

        o.events = self.events.copy()
        o.event_args = self.event_args.copy()
        o.properties = self.properties.copy()
        o.properties_dirty = self.properties_dirty.copy()

        o.children = []
        for c in self.children:
            o.append(c.clone(set_ui=set_ui, set_context=set_context))

        o.post_clone()
        return o

    def init(self):
        pass

    def post_clone(self):
        pass

    def nearest(self, predicate, exclude=None, descend=True):
        """
        Returns the nearest child which matches an arbitrary predicate lambda

        :param predicate: ``lambda element: bool``
        :type  predicate: function
        :param exclude: ``lambda element: bool`` - excludes matching branches from search
        :type  exclude: function, None
        :param descend: whether to descend inside matching elements
        :type  descend: bool
        """
        r = []
        q = [self]
        while len(q) > 0:
            e = q.pop(0)
            if exclude and exclude(e):
                continue
            if predicate(e):
                r.append(e)
                if not descend and e is not self:
                    continue
            q.extend(e.children)
        return r

    def find(self, id):
        """
        :param id: element ID
        :type  id: str
        :returns: the nearest child with given ID or ``None``
        :rtype: :class:`UIElement`, None
        """
        r = self.nearest(lambda x: x.id == id)
        return r[0] if len(r) > 0 else None

    def find_uid(self, uid):
        """
        :param uid: element UID
        :type  uid: int
        :returns: the nearest child with given UID or ``None``
        :rtype: :class:`UIElement`, None
        """
        r = self.nearest(lambda x: x.uid == uid)
        return r[0] if len(r) > 0 else None

    def find_type(self, typeid):
        """
        :returns: the nearest child with given type ID or ``None``
        :rtype: :class:`UIElement`, None
        """
        r = self.nearest(lambda x: x.typeid == typeid)
        return r[0] if len(r) > 0 else None

    def contains(self, element):
        """
        Checks if the ``element`` is in the subtree of ``self``

        :param element: element
        :type  element: :class:`UIElement`
        """
        return len(self.nearest(lambda x: x == element)) > 0

    def path_to(self, element):
        """
        :returns: a list of elements forming a path from ``self`` to ``element``
        :rtype: list
        """
        r = []
        while element != self:
            r.insert(0, element)
            element = element.parent
        return r

    def render(self):
        """
        Renders this element and its subtree to JSON

        :rtype: dict
        """
        attributes = {
            'uid': self.uid,
            'typeid': self.typeid,
            'children': [c.render() for c in self.children if self.visible],
        }

        attr_defaults = {
            'visible': True,
            'client': False,
        }
        attr_map = {
            'children': '_c',
            'typeid': '_t',
            'style': '_s',
        }

        result = {}
        for key, value in attributes.iteritems():
            if attr_defaults.get(key, None) != value:
                result[attr_map.get(key, key)] = value

        for prop in self.properties:
            if self.property_definitions[prop].public:
                value = getattr(self, prop)
                if attr_defaults.get(prop, None) != value:
                    result[attr_map.get(prop, prop)] = value
        return result

    def on(self, event, handler, *args):
        """
        Binds event with ID ``event`` to ``handler``. ``*args`` will be passed to the ``handler``.
        :param event: event
        :type  event: str
        :param handler: handler
        :type  handler: function
        """
        self.events[event] = handler
        self.event_args[event] = args

    def has_updates(self):
        """
        Checks for pending UI updates
        """
        if self.children_changed or self.invalidated:
            return True
        if any(self.properties_dirty.values()):
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
        for property in self.properties:
            self.properties_dirty[property] = False
        if self.visible:
            for child in self.children:
                child.clear_updates()

    def invalidate(self):
        self.invalidated = True

    def broadcast(self, method, *args, **kwargs):
        """
        Calls ``method`` on every member of the subtree

        :param method: method
        :type  method: str
        """
        if hasattr(self, method):
            getattr(self, method)(*args, **kwargs)

        if not self.visible:
            return

        for child in self.children:
            child.broadcast(method, *args, **kwargs)

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
        if not self.visible:
            return False
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

        :param event: event name
        :type  event: str
        :param params: event arguments
        :type  params: dict, None
        """
        self_event = event.replace('-', '_')
        if hasattr(self, 'on_%s' % self_event):
            getattr(self, 'on_%s' % self_event)(**(params or {}))
        if event in self.events:
            self.events[event](*self.event_args[event], **(params or {}))

    def reverse_event(self, event, params=None):
        """
        Raises the event on this element by feeding it to the UI root (so that ``@on`` methods in ancestors will work).

        :param event: event name
        :type  event: str
        :param params: event arguments
        :type  params: dict
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

        :param child: child
        :type  child: :class:`UIElement`
        """
        if child in self.children:
            return
        self.children.append(child)
        child.parent = self
        self.children_changed = True

    def delete(self):
        """
        Detaches this element from its parent
        """
        self.parent.remove(self)

    def remove(self, child):
        """
        Detaches the ``child``

        :param child: child
        :type  child: :class:`UIElement`
        """
        self.children.remove(child)
        child.parent = None
        self.children_changed = True


@public
@plugin
class NullElement (UIElement):
    pass

