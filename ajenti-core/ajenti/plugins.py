import imp
import os
import logging
import traceback
import subprocess
import sys
import weakref

import ajenti
from ajenti.api import *
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
        return self.plugin_name in PluginManager.get(ajenti.context).get_order()

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
@service
class PluginManager (object):
    """
    Handles plugin loading and unloading
    """

    blacklist = []

    __plugins = {}
    __order = []
    __locations = {}

    def __init__(self, context):
        path = os.path.split(__file__)[0]
        self.locations = ajenti.plugin_sources

    # Plugin loader
    def get_all(self):
        return self.__plugins

    def __getitem__(self, name):
        return self.__plugins[name]

    def get_content_path(self, name, path):
        return os.path.join(self[name].location, name, path)

    def get_order(self):
        return self.__order

    def load_all(self):
        items = []
        for location in self.locations:
            items += [(x, location) for x in os.listdir(location)]

        for item in items:
            if os.path.exists(os.path.join(item[1], item[0], '__init__.py')):
                self.__locations[item[0]] = item[1]

        for plugin, location in self.__locations.iteritems():
            if not plugin in self.__plugins:
                self.load_recursive(plugin)

    def load_recursive(self, name):
        location = self.__locations[name]
        while True:
            try:
                return self.load(name, location)
            except PluginDependency.Unsatisfied as e:
                if e.dependency.plugin_name in self.get_all():
                    if self.get_all()[e.dependency.plugin_name].crash:
                        self.get_all()[name].crash = e
                        logging.warn('Plugin dependency unsatisfied: "%s" -> "%s"' %
                                    (name, e.dependency.plugin_name))
                        return
                try:
                    logging.debug('Preloading plugin dependency: "%s"' % e.dependency.plugin_name)
                    if not self.load_recursive(e.dependency.plugin_name):
                        self.get_all()[name].crash = e
                        return
                except:
                    raise

    def load(self, name, location):
        """
        Loads given plugin
        """
        logging.debug('Loading plugin "%s"' % name)
        try:
            try:
                mod = imp.load_module(
                    'ajenti.plugins.%s' % name,
                    *imp.find_module(name, [location])
                )
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
            info.location = location
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
            logging.warn(' *** [%s] Plugin error: "%s"' % (name, e))
        except PluginCrashed as e:
            logging.warn(' *** [%s] Plugin crashed: "%s"' % (name, e))
            print(e.traceback)
            info.crash = e
        except Dependency.Unsatisfied as e:
            logging.debug(' *** [%s] skipping due to "%s"' % (name, e))
            info.crash = e
        except PluginLoadError as e:
            logging.warn(' *** [%s] Plugin failed to load: "%s"' % (name, e))
            info.crash = e

