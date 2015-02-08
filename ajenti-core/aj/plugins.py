import imp
import logging
import os
import subprocess
import sys
import traceback
import weakref
import yaml

import aj
from aj.api import *
from aj.util import *


@public
class PluginProvider (object):
    def provide(self):
        raise NotImplementedError()


@public
class DirectoryPluginProvider (PluginProvider):
    def __init__(self, path):
        self.path = os.path.abspath(path)

    def provide(self):
        found_plugins = []
        for dir in os.listdir(self.path):
            path = os.path.join(self.path, dir)
            if os.path.isdir(path):
                if os.path.exists(os.path.join(path, 'plugin.yml')):
                    found_plugins.append(path)
        return found_plugins


@public
class PythonPathPluginProvider (PluginProvider):
    def __init__(self):
        pass

    def provide(self):
        found_plugins = []
        for path in sys.path:
            if os.path.isdir(path):
                logging.debug('Looking for plugins in %s' % path)
                found_plugins += DirectoryPluginProvider(path).provide()
        return found_plugins


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

    def __init__(self, module_name=None):
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

    def __init__(self, plugin_name=None):
        self.plugin_name = plugin_name

    def is_satisfied(self):
        # get_order() only contains successfully loaded plugins
        return self.plugin_name in PluginManager.get(aj.context).get_order()

    def __str__(self):
        return self.plugin_name


@public
class BinaryDependency (Dependency):
    description = 'Application binary'

    class Unsatisfied (Dependency.Unsatisfied):
        def reason(self):
            return '%s' % self.dependency.binary_name

    def __init__(self, binary_name=None):
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

    def __init__(self, file_name=None):
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
    __info = {}

    def __init__(self, context):
        self.context = context

    # Plugin loader
    def get_all(self):
        return self.__plugins

    def __getitem__(self, name):
        return self.__plugins[name]

    def get_content_path(self, name, path):
        return os.path.join(self[name].path, path)

    def get_order(self):
        return self.__order

    def load_all_from(self, providers):
        found = []
        for provider in providers:
            found += provider.provide()

        self.__info = {}
        for path in found:
            yml_info = yaml.load(open(os.path.join(path, 'plugin.yml')))
            self.__info[yml_info['name']] = {
                'info': yml_info,
                'path': path
            }

        for plugin, info in self.__info.iteritems():
            if not plugin in self.__plugins:
                self.load_recursive(plugin, info)

    def load_recursive(self, name, info):
        while True:
            try:
                return self.load(name, info)
            except PluginDependency.Unsatisfied as e:
                if e.dependency.plugin_name in self.get_all():
                    if self.get_all()[e.dependency.plugin_name].crash:
                        self.get_all()[name].crash = e
                        logging.warn(
                            'Plugin dependency unsatisfied: "%s" -> "%s"' % (name, e.dependency.plugin_name)
                        )
                        return
                try:
                    if e.dependency.plugin_name not in self.__info:
                        logging.warn(
                            'Plugin dependency unsatisfied: "%s" -> "%s"' % (name, e.dependency.plugin_name)
                        )
                        return
                    logging.debug('Preloading plugin dependency: "%s"' % e.dependency.plugin_name)
                    if not self.load_recursive(e.dependency.plugin_name, self.__info[e.dependency.plugin_name]):
                        self.get_all()[name].crash = e
                        return
                except:
                    raise

    def load(self, name, info):
        """
        Loads given plugin
        """
        logging.debug('Loading plugin "%s"' % name)
        try:
            plugin_info = PluginInfo(**info['info'])
            plugin_info.active = False
            plugin_info.name = name
            plugin_info.crash = None
            plugin_info.path = info['path']
            self.__plugins[name] = plugin_info

            for dependency in plugin_info.dependencies:
                dependency.check()

            plugin_info.active = True

            module_path, module_name = os.path.split(info['path'])

            try:
                mod = imp.load_module(
                    'aj.plugins.%s' % name,
                    *imp.find_module(module_name, [module_path])
                )
            except PluginFormatError:
                raise
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
            plugin_info.crash = e
        except Dependency.Unsatisfied as e:
            logging.debug(' *** [%s] skipping due to "%s"' % (name, e))
            plugin_info.crash = e
        except PluginLoadError as e:
            logging.warn(' *** [%s] Plugin failed to load: "%s"' % (name, e))
            plugin_info.crash = e

