import re
import os.path
import inspect

from ajenti.com import *
from ajenti.app.api import IContentProvider
from ajenti.app.api import IEventDispatcher
from ajenti.app.api import ICategoryProvider


def event(event_name):
    """ Decorator function to register event handlers

    >>> class a(object):
    ...     @event('some/event')
    ...     def test1 (self):
    ...         pass
    ...
    ...     @event('other/event')
    ...     def test2 (self):
    ...         pass
    >>> a._events
    {'other/event': 'test2', 'some/event': 'test1'}
    >>>
    """
    # Get parent exection frame
    frame = inspect.stack()[1][0]
    # Get locals from it
    locals = frame.f_locals

    if ((locals is frame.f_globals) or
        ('__module__' not in locals)):
        raise TypeError('@event() can only be used in class definition')

    loc_events = locals.setdefault('_events',{})

    def event_decorator(func):
        loc_events[event_name] = func.__name__
        return func
    #def event_decorator

    return event_decorator
#def event


class ModuleContent(Plugin):
    abstract = True
    implements(IContentProvider)

    def content_path(self):
        if self.path == '' or self.module == '':
            raise AttributeError('You should provide path/module information')
        norm_path = os.path.join(os.path.dirname(self.path),'files')
        return (self.module, norm_path)


class EventProcessor(object):
    implements(IEventDispatcher)

    def _get_event_handler(self, event):
        """
        >>> class Test(EventProcessor):
        ...     @event('test')
        ...     def test(self):
        ...         pass
        ...
        >>> t = Test()
        >>> t._get_event_handler('test')
        'test'
        >>>
        """
        for cls in self.__class__.mro():
            if '_events' in dir(cls):
                if event in cls._events:
                    return cls._events[event]
        return None

    def match_event(self, event):
        """ Returns True if class (or any parent class) could handle event

        >>> class Test(EventProcessor):
        ...     @event('test')
        ...     def test(self):
        ...         pass
        ...
        >>> t = Test()
        >>> t._get_event_handler('test')
        'test'
        >>> t.match_event('test')
        True
        >>> t.match_event('test2')
        False
        >>>
        """
        if self._get_event_handler(event) is not None:
            return True
        return False

    def event(self, event, *params, **kwparams):
        """
        >>> class Test(EventProcessor):
        ...     @event('test')
        ...     def test(self, *p, **kw):
        ...         print(kw)
        ...
        >>> t = Test()
        >>> t.event('test', value='test')
        {'value': 'test'}
        >>>
        """
        handler = self._get_event_handler(event)
        if handler is None:
            return
        try:
            handler = self.__getattribute__(handler)
        except AttributeError:
            return

        return handler(event, *params, **kwparams)


class SessionPlugin(Plugin):
    session_proxy = None

    def __init__(self):
        if self.session_proxy is None:
            self.session_proxy = self.app.session.proxy(self.__class__.__name__)

        if self.session_proxy.get('sp_estabilished', None) is None:
            self.session_proxy['sp_estabilished'] = 'yes'
            self.on_session_start()

    def __getattr__(self, name):
        # TODO: use regexps
        if name[0] == '_' and not name[1] == '_':
            return self.session_proxy.get(name, None)
        else:
            raise AttributeError("'%s' object has no attribute '%s'"%
                                  (self.__class__.__name__, name))

    def __setattr__(self, name, value):
        # TODO: use regexps
        if name[0] == '_' and not name[1] == '_':
            self.session_proxy[name] = value
        else:
            self.__dict__[name] = value

    def on_session_start(self):
        pass


class CategoryPlugin(SessionPlugin, EventProcessor):
    abstract = True

    implements(ICategoryProvider)

    text = 'Caption'
    description = 'Topic description'
    icon = '/dl/core/ui/category-icon.png'

    @property
    def category(self):
        return { 'text': self.text,
                 'description': self.description,
                 'icon': self.icon }

