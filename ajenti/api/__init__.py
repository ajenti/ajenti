import os
import inspect
import copy

import ajenti
from ajenti.plugins import manager, PluginContext

from reconfigure.items.ajenti import ConfigData


class PluginInfo:
    """
    Describes a loaded plugin package
    """

    def __init__(self, **kwargs):
        self.name = ''
        self.icon = None
        self.author = ''
        self.homepage = ''
        self.dependencies = []

        def init():
            pass

        self.init = init

        for k in kwargs:
            setattr(self, k, kwargs[k])

    def __cmp__(self, other):
        return cmp(self.name, other.name)

    def __hash__(self):
        return hash(self.name)


def plugin(cls):
    """
    A decorator to create plugin classes::

        @plugin
        class SomePlugin (ISomething):
            pass

    If the class has a ``verify`` method returning ``bool``, it's invoked. If the method returned ``False``, plugin is rejected and removed from implementation lists.

    If the class has a ``platforms`` attribute, which is a list of supported platform names, it's compared against the current runtime OS platform. If the current platform is not in the list, plugin is also rejected.

    Following class methods are injected.

    .. function:: .get(context=<current context>)

        :returns: any existing instance or creates a new one

    .. function:: .new(*args, context=<current context>, **kwargs)

        :returns: a new instance. Use this method instead of constructor, since it invokes the proper initialization chain and registers the instance

    """

    # Run custom verificator if any
    if hasattr(cls, 'verify'):
        if not cls.verify():
            return

    if hasattr(cls, 'platforms'):
        if not ajenti.platform in cls.platforms:
            return

    manager.register_implementation(cls)
    cls._plugin = True
    cls._path = inspect.getfile(cls)
    cls.classname = cls.__module__ + '.' + cls.__name__

    # Inject methods

    def get(cls, context=None):
        if not context:
            context = extract_context()
        return context.get_instance(cls)
    cls.get = get.__get__(cls)

    def new(cls, *args, **kwargs):
        context = kwargs.pop('context', None)
        if not context:
            context = extract_context()
        return context.instantiate(cls, *args, **kwargs)
    cls.new = new.__get__(cls)

    if hasattr(cls, 'classinit'):
        cls.classinit()

    return cls


def _check_plugin(cls):
    if not hasattr(cls, '_plugin'):
        raise Exception('Class %s must be decorated with @plugin' % cls)


def interface(cls):
    """
    A decorator to create plugin interfaces::

        @interface
        class ISomething (object):
            def contract(self):
                pass

    Following class methods are injected:

    .. function:: .get(context=<current context>)

        :returns: any existing instance or creates a new one

    .. function:: .get_all(context=<current context>)

        :returns: list of instances for each implementation

    .. function:: .get_class()

        :returns: any implementation class

    .. function:: .get_classes()

        :returns: list of implementation classes

    .. function:: .get_instances(context=<current context>)

        :returns: list of all existing instances

    """

    # Inject methods

    def get(cls, context=None):
        if not context:
            context = extract_context()
        impls = manager.get_implementations(cls)
        if len(impls) == 0:
            raise Exception('Implementations for %s not found' % cls.__name__)
        return context.get_instance(impls[0])
    cls.get = get.__get__(cls)

    def get_all(cls, context=None):
        if not context:
            context = extract_context()
        return [context.get_instance(x) for x in manager.get_implementations(cls)]
    cls.get_all = get_all.__get__(cls)

    def get_class(cls):
        return manager.get_implementations(cls)[0]
    cls.get_class = get_class.__get__(cls)

    def get_classes(cls):
        return manager.get_implementations(cls)
    cls.get_classes = get_classes.__get__(cls)

    def get_instances(cls, context=None):
        if not context:
            context = extract_context()
        return context.get_instances(cls)
    cls.get_instances = get_instances.__get__(cls)

    cls._interface = True
    manager.register_interface(cls)

    return cls


def extract_context():
    """
    An utility function that extracts and returns the nearest :class:`AppContext` from the current call stack.
    """
    for frame in inspect.stack():
        # Traverse the call stack
        arguments = frame[0].f_code.co_varnames
        if not arguments:
            continue
        self_argument = arguments[0]  # This *should* be 'self'
        if not self_argument in frame[0].f_locals:
            continue
        instance = frame[0].f_locals[self_argument]  # = first passed *arg
        if hasattr(instance, 'context') and isinstance(instance.context, PluginContext):
            # Grab the context if any
            return instance.context


@interface
class BasePlugin (object):
    """
    A base plugin class that provides :class:`AppContext` and ``classconfig`` functionality.
    """

    default_classconfig = None
    """ Override this in your class with a default config object (must be JSON-serializable) """

    classconfig_name = None
    """ Override this in your class if you want this plugin to be configurable through Configure > Plugins """

    classconfig_root = False
    """ When True, classconfig will be stored in root's config section disregarding current user """

    classconfig_editor = None
    """ Override this in your class with an ajenti.plugins.configurator.api.ClassConfigEditor derivative """

    context = None
    """ Automatically receives a reference to the current :class:`AppContext` """

    def init(self):
        """
        Do your initialization here. Correct bottom-to-up inheritance call order guaranteed.
        """
        self.context = extract_context()

        if self.context:
            self.load_classconfig()

    def load_classconfig(self):
        """
        Loads the content of ``classconfig`` attribute from the user's configuration section.
        """
        config = ConfigData()
        config.name = self.classname
        config.data = copy.deepcopy(self.default_classconfig)
        if self.default_classconfig:
            self.classconfig = self.__get_config_store().setdefault(self.classname, config).data

    def __get_config_store(self):
        if not self.classconfig_root:
            return self.context.user.configs
        return ajenti.config.tree.users['root'].configs

    def open_content(self, path, mode='r'):
        """
        Provides access to plugin-specific files from ``/content`` directory of the package

        :param path: path relative to package's ``/content``
        :param mode: Python file access mode
        :returns: An open file object
        """
        _check_plugin(self.__class__)

        root = os.path.split(self.__class__._path)[0]
        while len(root) > 1 and not os.path.exists(os.path.join(root, 'content')):
            root = os.path.split(root)[0]
        if len(root) <= 1:
            raise Exception('content directory not found')
        return open(os.path.join(root, 'content', path), mode)

    def save_classconfig(self):
        """
        Saves the content of ``classconfig`` attribute into the user's configuration section.
        """
        self.__get_config_store()[self.classname].data = self.classconfig
        ajenti.config.save()


class AppContext (PluginContext):
    """
    A session-specific context provided to everyone who inherits :class:`BasePlugin`.

    .. attribute:: session

        current HTTP session: :class:`ajenti.middleware.Session`

    .. attribute:: user

        current logged in user: :class:`reconfigure.items.ajenti.UserData`

    Methods injected by MainPlugin:

    .. method:: notify(text)

        :param text: Notification text to show

    .. method:: launch(id, *args, **kwargs)

        :param id: Intent ID to be launched
    """

    def __init__(self, parent, httpcontext):
        PluginContext.__init__(self)
        self.parent = parent
        self.session = httpcontext.session
        self.user = ajenti.config.tree.users[httpcontext.session.identity]

    def __str__(self):
        return 'Context for %s' % self.user.name


__all__ = [
    'PluginInfo',
    'BasePlugin',
    'AppContext',
    'plugin',
    'extract_context',
    'interface',
]
