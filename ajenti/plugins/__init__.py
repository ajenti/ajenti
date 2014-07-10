import imp
import os
import logging
import traceback
import subprocess
import sys
import weakref

from ajenti.util import *


@public
class PluginLoadError (Exception):
    pass


@public
class PluginFormatError (PluginLoadError):
    def describe(self):
        return 'Plugin format error'

    def __str__(self):
        return 'format error'


@public
class PluginCrashed (PluginLoadError):
    def __init__(self, e):
        self.e = e
        self.traceback = traceback.format_exc()

    def describe(self):
        return 'Crashed: %s' % self.e

    def __str__(self):
        return 'crashed: %s' % self.e


@public
class Dependency (object):
    class Unsatisfied (PluginLoadError):
        def __init__(self):
            PluginLoadError.__init__(self, None)
            self.dependency = None

        def reason(self):
            pass

        def describe(self):
            return 'Dependency unsatisfied'

        def __str__(self):
            return '%s (%s)' % (self.dependency.__class__.__name__, self.reason())

    def satisfied(self):
        if hasattr(self, '_was_satisfied'):
            return self._was_satisfied
        self._was_satisfied = self.is_satisfied()
        return self._was_satisfied

    def build_exception(self):
        exception = self.Unsatisfied()
        exception.dependency = self
        return exception

    def check(self):
        if not self.satisfied():
            exception = self.build_exception()
            raise exception

    @property
    def value(self):
        return str(self)


@public
class ModuleDependency (Dependency):
    description = 'Python module'

    class Unsatisfied (Dependency.Unsatisfied):
        def reason(self):
            return '%s' % self.dependency.module_name

    def __init__(self, module_name):
        self.module_name = module_name

    def is_satisfied(self):
        if self.module_name in sys.modules:
            return True
        try:
            __import__(self.module_name)
            return True
        except:
            return False

    def __str__(self):
        return self.module_name


@public
class PluginDependency (Dependency):
    description = 'Plugin'

    class Unsatisfied (Dependency.Unsatisfied):
        def reason(self):
            return '%s' % self.dependency.plugin_name

    def __init__(self, plugin_name):
        self.plugin_name = plugin_name

    def is_satisfied(self):
        # get_order() only contains successfully loaded plugins
        return self.plugin_name in manager.get_order()

    def __str__(self):
        return self.plugin_name


@public
class BinaryDependency (Dependency):
    description = 'Application binary'

    class Unsatisfied (Dependency.Unsatisfied):
        def reason(self):
            return '%s' % self.dependency.binary_name

    def __init__(self, binary_name):
        self.binary_name = binary_name

    def is_satisfied(self):
        return subprocess.call(['which', self.binary_name]) == 0

    def __str__(self):
        return self.binary_name


@public
class FileDependency (Dependency):
    description = 'File'

    class Unsatisfied (Dependency.Unsatisfied):
        def reason(self):
            return '%s' % self.dependency.file_name

    def __init__(self, file_name):
        self.file_name = file_name

    def is_satisfied(self):
        return os.path.exists(self.file_name)

    def __str__(self):
        return self.file_name


@public
class PluginContext (object):
    """
    Container of interfaces and plugins
    """

    def __init__(self):
        self.__instances = {}
        self.__hardrefs = []

    def __str__(self):
        return 'Root context'

    def _get_all_instances(self):
        return self.__instances

    def vacuum_instances(self):
        dead_ifaces = []
        for iface, lst in self.__instances.iteritems():
            for ref in list(lst):
                if ref() is None:
                    lst.remove(ref)
            if len(lst) == 0:
                dead_ifaces.append(iface)
        for iface in dead_ifaces:
            del self.__instances[iface]

    def get_instances(self, cls):
        return filter(None, [_() for _ in self.__instances.setdefault(cls, [])])

    def get_instance(self, cls):
        self.vacuum_instances()
        if not cls in self.__instances:
            return self.instantiate(cls)
        inst = list(self.__instances[cls])[0]()
        if inst is None:
            return self.instantiate(cls)
        return inst

    def instantiate(self, cls, *args, **kwargs):
        instance = cls(*args, **kwargs)
        instance.context = self
        last_init = None
        for base in reversed(cls.mro()):
            if hasattr(base, 'init'):
                init = getattr(base, 'init')
                if init != last_init:
                    init(instance)
                    last_init = init

        nit = getattr(cls, '_no_instance_tracking', None)
        if nit is not True and nit != cls:
            logging.debug('%s instantiated [%s] %s' % (self, type(instance).__name__, instance))
            for iface in cls._implements + [cls]:
                if not getattr(iface, '_no_instance_tracking', None) in [True, iface]:
                    self.__instances.setdefault(iface, set()).add(weakref.ref(instance))

        if hasattr(cls, '_instance_hardref'):
            self.__hardrefs.append(instance)

        return instance


@public
class PluginManager:
    """
    Handles plugin loading and unloading
    """

    extra_location = '/var/lib/ajenti/plugins'
    context = PluginContext()
    blacklist = []

    __classes = {}
    __plugins = {}
    __order = []

    def register_interface(self, iface):
        setattr(iface, '__ajenti_interface', True)

    def register_implementation(self, impl):
        impl._implements = []
        for cls in impl.mro():
            if hasattr(cls, '__ajenti_interface'):
                self.__classes.setdefault(cls, []).append(impl)
                impl._implements.append(cls)

    def get_implementations(self, iface):
        return filter(lambda x: x not in self.blacklist, self.__classes.setdefault(iface, []))

    # Plugin loader
    def get_all(self):
        return self.__plugins

    def get_order(self):
        return self.__order

    def load_all(self):
        path = os.path.split(__file__)[0]

        locations = [path]
        if os.path.exists(self.extra_location):
            locations += [self.extra_location]
        
        items = []
        for location in locations:
            items += [(x, os.path.join(location, x)) for x in os.listdir(location)]

        for item in items:
            if os.path.exists(os.path.join(item[1], '__init__.py')):
                if not item[0] in self.__plugins:
                    self.load_recursive(item[0])

    def get_plugins_root(self):
        return os.path.split(__file__)[0]

    def resolve_path(self, name):
        return self.__plugins[name].path

    def load_recursive(self, name):
        while True:
            try:
                return self.load(name)
            except PluginDependency.Unsatisfied as e:
                if e.dependency.plugin_name in manager.get_all():
                    if manager.get_all()[e.dependency.plugin_name].crash:
                        manager.get_all()[name].crash = e
                        logging.warn(' *** Plugin dependency unsatisfied: %s -> %s' %
                                    (name, e.dependency.plugin_name))
                        return
                try:
                    logging.debug('Preloading plugin dependency: %s' % e.dependency.plugin_name)
                    if not self.load_recursive(e.dependency.plugin_name):
                        manager.get_all()[name].crash = e
                        return
                except:
                    raise

    def load(self, name):
        """
        Loads given plugin
        """
        logging.debug('Loading plugin %s' % name)
        try:
            try:
                mod = imp.load_module('ajenti.plugins.%s' % name,
                                      *imp.find_module(name, [self.get_plugins_root(), self.extra_location]))
                if not hasattr(mod, 'info'):
                    raise PluginFormatError()
            except PluginFormatError:
                raise
            except Exception as e:
                # TOTAL CRASH
                from ajenti.api import PluginInfo
                info = PluginInfo(name=name, crash=e)
                self.__plugins[name] = info
                raise PluginCrashed(e)

            info = mod.info
            info.module = mod
            info.active = False
            info.name = name
            info.path = mod.__path__[0]
            info.crash = None
            if hasattr(mod, 'init'):
                info.init = mod.init
            self.__plugins[name] = info

            for dependency in info.dependencies:
                dependency.check()
            info.active = True

            try:
                info.init()
            except Exception as e:
                raise PluginCrashed(e)

            if name in self.__order:
                self.__order.remove(name)
            self.__order.append(name)

            return True
        except PluginDependency.Unsatisfied as e:
            raise
        except PluginFormatError as e:
            logging.warn(' *** [%s] Plugin error: %s' % (name, e))
        except PluginCrashed as e:
            logging.warn(' *** [%s] Plugin crashed: %s' % (name, e))
            print(e.traceback)
            info.crash = e
        except Dependency.Unsatisfied as e:
            logging.warn(' *** [%s] skipping due to %s' % (name, e))
            info.crash = e
        except PluginLoadError as e:
            logging.warn(' *** [%s] Plugin failed to load: %s' % (name, e))
            info.crash = e


manager = PluginManager()
