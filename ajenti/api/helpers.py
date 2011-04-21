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
        pass


class CategoryPlugin(SessionPlugin, EventProcessor):
    abstract = True

    implements(ICategoryProvider)

    text = 'Caption'
    icon = '/dl/core/ui/catfolders/other.png'
    folder = 'other'

    is_enabled = None
    
    def test(self):
        return True
    
    def on_init(self):
        pass

    def get_counter(self):
        pass
        
    def get_config(self):
        try:
            return self.app.get_config(self)
        except:
            return None
            
    def put_message(self, cls, msg):
        if not self.app.session.has_key('messages'):
            self.app.session['messages'] = []
        self.app.session['messages'].append((cls, msg))
            
            
class ModuleConfig(Plugin):
    abstract = True
    implements(IModuleConfig)
    
    labels = {}
    
    def overlay_config(self):
        section = 'cfg_' + self.plugin
        for k in self.__class__.__dict__:
            if not k in ['platform', 'plugin', 'labels'] and not k.startswith('_'):
                if self.app.config.has_option(section, k):
                    setattr(self, k, eval(self.app.config.get(section, k)))
            
    def save(self):
        section = 'cfg_' + self.plugin
        for k in self.__class__.__dict__:
            if not k in ['platform', 'plugin', 'labels'] and not k.startswith('_'):
                if getattr(self, k) != getattr(self.__class__, k):
                    self.app.config.set(section, k, repr(getattr(self, k)))
                else:
                    self.app.config.remove_option(section, k)
        self.app.config.save()
                
    def get_ui_edit(self):
        t = UI.LayoutTable()
        for k in self.__class__.__dict__:
            if not k in ['platform', 'plugin', 'labels'] and not k.startswith('_'):
                val = getattr(self, k)
                lbl = k 
                if k in self.labels:
                    lbl = self.labels[k]
                if type(val) is bool:
                    t.append(UI.LayoutTableRow(
                        UI.LayoutTableCell(
                            UI.CheckBox(text=lbl, name=k, checked=val),
                            colspan=2
                        )
                    ))
                if type(val) is str:
                    t.append(UI.LayoutTableRow(
                        UI.Label(text=lbl),
                        UI.TextInput(name=k, value=val)
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

