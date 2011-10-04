import re
import os.path
import inspect
import traceback

from ajenti.com import *
from ajenti.api import *
from ajenti.ui import *


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


class EventProcessor(object):
    """
    A base class for plugins suitable for handling UI Events_.
    You will need to decorate handler methods with :func:`event`.
    """
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
        Calls a handler method suitable for given event.

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
    """
    A base class for plugins attached to the current user's session.

    Instance variables starting with '_' will be automatically [re]stored
    from/into the session.

    """

    session_proxy = None

    def __init__(self):
        if self.session_proxy is None:
            self.session_proxy = self.app.session.proxy(self.__class__.__name__)

        if self.session_proxy.get('sp_estabilished', None) is None:
            self.session_proxy['sp_estabilished'] = 'yes'
            try:
                self.on_session_start()
            except Exception, e:
                traceback.print_exc()
                raise

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
        """
        Called when a session is estabilished for new user or a new plugin
        is attached to the session for the first time.
        """


class CategoryPlugin(SessionPlugin, EventProcessor):
    """
    A base class for plugins providing sidebar entry

    - ``text`` - `str`, sidebar entry text
    - ``icon`` - `str`, sidebar icon URL
    - ``folder`` - `str`, sidebar section name (lowercase)
    """
    abstract = True

    implements(ICategoryProvider)

    text = 'Caption'
    icon = '/dl/core/ui/catfolders/other.png'
    folder = 'other'

    def on_init(self):
        """
        Called when a web request has arrived and this plugin is active (visible).
        """

    def get_counter(self):
        """
        May return short string to be displayed in 'bubble' right to the sidebar
        entry.

        :returns: None or str
        """

    def get_config(self):
        """
        Returns a most preferred ModuleConfig for this class.

        :returns:   :class:`ModuleConfig` or None
        """
        try:
            return self.app.get_config(self)
        except:
            return None

    def put_message(self, cls, msg):
        """
        Pushes a visual message to the message queue.
        All messages will be displayed on the next webpage update user will
        receive.

        :param  cls:    one of 'info', 'warn', 'err'
        :type   cls:    str
        :params msg:    message text
        """
        if not self.app.session.has_key('messages'):
            self.app.session['messages'] = []
        self.app.session['messages'].append((cls, msg))


class ModuleConfig(Plugin):
    """
    Base class for simple "configs" for different platforms for the plugins.

    - ``target`` - `type`, :class:`ajenti.com.Plugin` class for which this config
      is targeted.
    - ``labels`` - `dict(str:str)` - text labels for visual editing of each property.

    All other properties are considered ModuleConfig parameters - they are shown
    in the UI and saved to config files.
    """
    abstract = True
    implements(IModuleConfig)

    target = None
    labels = {}

    def overlay_config(self):
        section = 'cfg_' + self.target.__name__
        for k in self.__class__.__dict__:
            if not k in ['platform', 'plugin', 'labels'] and not k.startswith('_'):
                if self.app.config.has_option(section, k):
                    setattr(self, k, eval(self.app.config.get(section, k)))

    def save(self):
        section = 'cfg_' + self.target.__name__
        for k in self.__class__.__dict__:
            if not k in ['platform', 'plugin', 'labels'] and not k.startswith('_'):
                if getattr(self, k) != getattr(self.__class__, k):
                    self.app.config.set(section, k, repr(getattr(self, k)))
                else:
                    self.app.config.remove_option(section, k)
        self.app.config.save()

    def get_ui_edit(self):
        t = UI.Container()
        for k in self.__class__.__dict__:
            if not k in ['platform', 'plugin', 'labels'] and not k.startswith('_'):
                val = getattr(self, k)
                lbl = k
                if k in self.labels:
                    lbl = self.labels[k]
                if type(val) is bool:
                    t.append(UI.Formline(
                        UI.CheckBox(name=k, checked=val),
                        text=lbl
                    ))
                if type(val) is str:
                    t.append(UI.Formline(
                        UI.TextInput(name=k, value=val),
                        text=lbl,
                    ))
        return UI.DialogBox(t, id='dlgEditModuleConfig')

    def apply_vars(self, vars):
        for k in vars:
            if not k in ['action'] and not k.startswith('_'):
                nval = vars.getvalue(k, None)
                oval = getattr(self, k)
                if type(oval) is str:
                    setattr(self, k, nval)
                if type(oval) is bool:
                    setattr(self, k, nval=='1')
