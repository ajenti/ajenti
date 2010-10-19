# encoding: utf-8
#
# Copyright (C) 2007-2010 Dmitry Zamaruev (dmitry.zamaruev@gmail.com)


import inspect
import traceback

from PrioList import PrioList


class Interface (property):
    """ Base abstract class for all interfaces

    Could be used as callable (decorator)
    to check if Plugin implements all methods
    (internal use only)
    """
    def __init__(self, interface=None, filter_func=None):
        if interface is not None:
            # Assume property invocation
            property.__init__(self, self._plugins)
            self.filter_func = filter_func
            self.interface = interface
            self.__doc__ = 'Plugins list for "%s"'%interface.__name__

    def _plugins(self, plugin):
        """ Returns a list of currently registered plugins
            for requested interface
        """
        pm = plugin.plugin_manager
        plugins = pm.plugin_get(self.interface)
        if self.filter_func:
            plugins = filter(self.filter_func, plugins)
        return filter(None, [pm.instance_get(cls, True) for cls in plugins])

    def __call__(self, cls):
        # Check that target class supports all our interface methods
        cls_methods = [m for m in dir(cls) if not m.startswith('_')]

        # Check local interface methods
        methods = [m for m in dir(self.__class__) if not m.startswith('_')]
        # Filter out property methods
        methods = [m for m in methods if m not in dir(property)]

        for method in methods:
            if method not in cls_methods:
                raise AttributeError(
                      "%s implementing interface %s, does not have '%s' method"%
                      (cls, self.__class__, method))


def implements (*interfaces):
    # Get parent exection frame
    frame = inspect.stack()[1][0]
    # Get locals from it
    locals = frame.f_locals

    if ((locals is frame.f_globals) or
        ('__module__' not in locals)):
        raise TypeError('implements() can only be used in class definition')

    if '_implements' in locals:
        raise TypeError('implements() could be used only once')

    locals.setdefault('_implements',[]).extend(interfaces)
    # TODO: trac also all base interfaces (if needed)


class PluginManager (object):
    """ Holds all registered classes, instances and implementations
    You should have one class instantiated from both PluginManager and Plugin
    to trigger plugins magick
    """
    # Class-wide properties
    __classes = []
    __plugins = {}

    def __init__(self):
        self.__instances = {}

    @staticmethod
    def class_register (cls):
        PluginManager.__classes.append(cls)

    @staticmethod
    def class_list ():
        return PluginManager.__classes

    @staticmethod
    def plugin_list ():
        return PluginManager.__plugins

    @staticmethod
    def plugin_register (iface, cls):
        PluginManager.__plugins.setdefault(iface,PrioList()).append(cls)

    @staticmethod
    def plugin_get (iface):
        return PluginManager.__plugins.get(iface, [])

    def instance_get(self, cls, instantiate=False):
        if not self.plugin_enabled(cls):
            return None
        inst = self.__instances.get(cls)
        if instantiate == True and inst is None:
            if cls not in PluginManager.__classes:
                raise Exception('Class "%s" is not registered'% cls.__name__)
            try:
                inst = cls(self)
            except TypeError, e:
                print traceback.format_exc()
                raise Exception('Unable instantiate plugin %r (%s)'%(cls, e))
                
        return inst

    def instance_set(self, cls, inst):
        self.__instances[cls] = inst

    def instance_list(self):
        return self.__instances

    def plugin_enabled(self, cls):
        return True

    def plugin_activated(self, plugin):
        pass


class MetaPlugin (type):
    """ MetaClass for Plugin
    """

    def __new__ (cls, name, bases, d):
        """ Create new class """

        # Create new class
        new_class = type.__new__(cls, name, bases, d)

        # If we creating base class, do nothing
        if name == 'Plugin':
            return new_class

        # Override __init__ for Plugins, for instantiation process
        if True not in [issubclass(x, PluginManager) for x in bases]:
            # Allow Plugins to have own __init__ without parameters
            init = d.get('__init__')
            if not init:
                # Because we're replacing the initializer, we need to make sure
                # that any inherited initializers are also called.
                for init in [b.__init__._original for b in new_class.mro()
                             if issubclass(b, Plugin)
                             and '__init__' in b.__dict__]:
                    break
            def maybe_init(self, plugin_manager, init=init, cls=new_class):
                if plugin_manager.instance_get(cls) is None:
                    # Plugin is just created
                    if init:
                        try:
                            init(self)
                        except:
                            raise
                    if not self.multi_instance:
                        plugin_manager.instance_set(cls, self)
            maybe_init._original = init
            new_class.__init__ = maybe_init

        # If this is abstract class, do no record it
        if d.get('abstract'):
            return new_class

        # Save created class for future reference
        PluginManager.class_register(new_class)

        # Collect all interfaces that this class implements
        interfaces = d.get('_implements',[])
        for base in [base for base in new_class.mro()[1:] if hasattr(base, '_implements')]:
            interfaces.extend(base._implements)

        # Delete duplicates, in case we inherit same Intarfaces
        # or we need to override priority
        _ints = []
        _interfaces = []
        for interface in interfaces:
            _int = interface
            if isinstance(interface, tuple):
                _int = interface[0]

            if _int not in _ints:
                _ints.append(_int)
                _interfaces.append(interface)

        interfaces = _interfaces

        # Check that class supports all needed methods
        for interface in interfaces:
            _int = interface
            if isinstance(interface, tuple):
                _int = interface[0]
            _int()(new_class)

        # Register plugin
        for interface in interfaces:
            if isinstance(interface, tuple):
                PluginManager.plugin_register(interface[0], (new_class, interface[1]))
            else:
                PluginManager.plugin_register(interface, new_class)

        return new_class

#class MetaPlugin


class Plugin (object):
    """ Base class for all plugins """

    __metaclass__ = MetaPlugin

    multi_instance = False

    platform = ['any']
    
    
    def __new__(cls, *args, **kwargs):
        """ Returns a class instance,
        If it already instantiated, return it
        otherwise return new instance
        """
        if issubclass(cls, PluginManager):
            # If we also a PluginManager, just create and return
            self = super(Plugin, cls).__new__(cls)
            self.plugin_manager = self
            return self

        # Normal case when we are standalone plugin
        self = None
        plugin_manager = args[0]
        if not cls.multi_instance:
            self = plugin_manager.instance_get(cls)

        if self is None:
            self = super(Plugin, cls).__new__(cls)
            self.plugin_manager = plugin_manager
            self.plugin_id = cls.__name__.lower()
            # Allow PluginManager implementation to update Plugin
            plugin_manager.plugin_activated(self)

        return self
        
