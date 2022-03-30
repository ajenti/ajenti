import importlib.util
import logging
import os
import subprocess
import sys
import traceback
import yaml
from jadi import service

import aj
from aj.util import public


@public
class PluginProvider():
    """
    A base class for plugin locator
    """

    def provide(self):
        """
        Should return a list of found plugin paths

        :returns: list(str)
        """
        raise NotImplementedError()


@public
class DirectoryPluginProvider(PluginProvider):
    """
    A plugin provider that looks up plugins in a given directory.

    :param path: directory to look for plugins in
    """

    def __init__(self, path):
        self.path = os.path.abspath(path)

    def provide(self):
        found_plugins = []
        if os.path.exists(os.path.join(self.path, 'plugin.yml')):
            found_plugins.append(self.path)

        for _dir in os.listdir(self.path):
            path = os.path.join(self.path, _dir)
            if os.path.isdir(path):
                if os.path.exists(os.path.join(path, 'plugin.yml')):
                    found_plugins.append(path)

        return found_plugins


@public
class PythonPathPluginProvider(PluginProvider):
    """
    A plugin provider that looks up plugins on ``$PYTHONPATH``
    """

    def __init__(self):
        pass

    def provide(self):
        found_plugins = []
        for path in sys.path:
            if os.path.isdir(path):
                logging.debug(f'Looking for plugins in {path}')
                found_plugins += DirectoryPluginProvider(path).provide()
        return found_plugins


@public
class PluginLoadError(Exception):
    pass


@public
class PluginCrashed(PluginLoadError):
    def __init__(self, exception):
        PluginLoadError.__init__(self)
        self.exception = exception
        self.traceback = traceback.format_exc()

    def describe(self):
        return f'Crashed: {repr(self.exception)}'

    def __str__(self):
        return f'crashed: {repr(self.exception)}'


@public
class Dependency(yaml.YAMLObject):
    yaml_loader = yaml.SafeLoader
    yaml_tag = u'!Dependency'

    class Unsatisfied(PluginLoadError):
        def __init__(self):
            PluginLoadError.__init__(self, None)
            self.dependency = None

        def reason(self):
            pass

        def describe(self):
            return 'Dependency unsatisfied'

        def __str__(self):
            return f'{self.dependency.__class__.__name__} ({self.reason()})'

    def build_exception(self):
        exception = self.Unsatisfied()
        exception.dependency = self
        return exception

    def check(self):
        if not self.is_satisfied():
            exception = self.build_exception()
            raise exception

    @property
    def value(self):
        return str(self)


@public
class ModuleDependency(Dependency):
    description = 'Python module'
    yaml_tag = u'!ModuleDependency'

    class Unsatisfied(Dependency.Unsatisfied):
        def reason(self):
            return f'{self.dependency.module_name}'

    def __init__(self, module_name=None):
        self.module_name = module_name

    def is_satisfied(self):
        if self.module_name in sys.modules:
            return True
        try:
            __import__(self.module_name)
            return True
        except ImportError:
            return False

    def __str__(self):
        return self.module_name


@public
class PluginDependency(Dependency):
    description = 'Plugin'
    yaml_tag = u'!PluginDependency'

    class Unsatisfied(Dependency.Unsatisfied):
        def reason(self):
            return f'{self.dependency.plugin_name}'

    def __init__(self, plugin_name=None):
        self.plugin_name = plugin_name

    def is_satisfied(self):
        return self.plugin_name in PluginManager.get(aj.context).get_loaded_plugins_list()

    def __str__(self):
        return self.plugin_name


@public
class OptionalPluginDependency(Dependency):
    description = 'Plugin'
    yaml_tag = u'!OptionalPluginDependency'

    class Unsatisfied(Dependency.Unsatisfied):
        def reason(self):
            return f'{self.dependency.plugin_name}'

    def __init__(self, plugin_name=None):
        self.plugin_name = plugin_name

    def is_satisfied(self):
        return True

    def __str__(self):
        return self.plugin_name


@public
class BinaryDependency(Dependency):
    description = 'Application binary'
    yaml_tag = u'!BinaryDependency'

    class Unsatisfied(Dependency.Unsatisfied):
        def reason(self):
            return f'{self.dependency.binary_name}'

    def __init__(self, binary_name=None):
        self.binary_name = binary_name

    def is_satisfied(self):
        return subprocess.call(['which', self.binary_name]) == 0

    def __str__(self):
        return self.binary_name


@public
class FileDependency(Dependency):
    description = 'File'
    yaml_tag = u'!FileDependency'

    class Unsatisfied(Dependency.Unsatisfied):
        def reason(self):
            return f'{self.dependency.file_name}'

    def __init__(self, file_name=None):
        self.file_name = file_name

    def is_satisfied(self):
        return os.path.exists(self.file_name)

    def __str__(self):
        return self.file_name


@public
@service
class PluginManager():
    """
    Handles plugin loading and unloading
    """

    __plugin_info = {}
    __crashes = {}

    def __init__(self, context):
        self.context = context
        self.load_order = []

    def get_crash(self, name):
        return self.__crashes.get(name, None)

    def __getitem__(self, name):
        return self.__plugin_info[name]

    def __iter__(self):
        return iter(self.load_order)

    def __len__(self):
        return len(self.__plugin_info)

    def get_content_path(self, name, path):
        path = path.replace('..', '').strip('/')
        return os.path.join(self[name]['path'], path)

    def get_loaded_plugins_list(self):
        for plugin in self:
            if self[plugin]['imported']:
                yield self[plugin]['info']['name']

    def load_all_from(self, providers):
        """
        Loads all plugins provided by given providers.

        :param providers:
        :type providers: list(:class:`PluginProvider`)
        """
        found = []
        for provider in providers:
            found += provider.provide()

        self.__plugin_info = {}
        for path in found:
            yml_info = yaml.load(open(os.path.join(path, 'plugin.yml')), Loader=yaml.SafeLoader)
            yml_info['resources'] = [
                ({'path': x} if isinstance(x, str) else x)
                for x in yml_info.get('resources', [])
            ]
            self.__plugin_info[yml_info['name']] = {
                'info': yml_info,
                'path': path,
                'imported': False,
            }

        logging.info(f'Discovered {len(self.__plugin_info):d} plugins')

        self.load_order = []
        to_load = list(self.__plugin_info.values())

        while True:
            delta = 0
            for plugin in to_load:
                for dep in plugin['info']['dependencies']:
                    if isinstance(dep, PluginDependency) and dep.plugin_name not in self.load_order:
                        break
                    if isinstance(dep, OptionalPluginDependency) and dep.plugin_name not in self.load_order:
                        break
                else:
                    self.load_order.append(plugin['info']['name'])
                    to_load.remove(plugin)
                    delta += 1

            if delta == 0:
                # less strict
                for plugin in to_load:
                    for dep in plugin['info']['dependencies']:
                        if isinstance(dep, PluginDependency) and dep.plugin_name not in self.load_order:
                            break
                    else:
                        self.load_order.append(plugin['info']['name'])
                        to_load.remove(plugin)
                        delta += 1

            if delta == 0:
                break

        for plugin in to_load:
            for dep in plugin['info']['dependencies']:
                if isinstance(dep, PluginDependency) and dep.plugin_name not in self.load_order:
                    self.__crashes[plugin['info']['name']] = dep.build_exception()
                    logging.warning(f"Not loading [{plugin['info']['name']}] because [{dep.plugin_name}] is unavailable")

        for name in list(self.load_order):
            try:
                for dependency in self[name]['info']['dependencies']:
                    if not isinstance(dependency, PluginDependency):
                        dependency.check()
            except Dependency.Unsatisfied as e:
                self.__crashes[name] = e
                logging.warning(f'Not loading [{name}] because dependency failed: {e}')
                self.load_order.remove(name)

        logging.debug(f'Resolved load order for {len(self.load_order):d} plugins: {self.load_order}')

        for name in list(self.load_order):
            try:
                self.__import_plugin_module(name, self[name])
            except Exception as e:
                self.__crashes[name] = PluginCrashed(e)
                logging.error(f'[{name}]: plugin import failed: {e}')
                logging.error(traceback.format_exc())
                self.load_order.remove(name)

        for name in list(self.load_order):
            try:
                self.__init_plugin_module(name, self[name])
            except Exception as e:
                self.__crashes[name] = PluginCrashed(e)
                logging.error(f'[{name}]: plugin init failed: {e}')
                logging.error(traceback.format_exc())
                self.load_order.remove(name)

        logging.info(f'Loaded {len(self.load_order):d} plugins')

    def __import_plugin_module(self, name, info):
        logging.debug(f'Importing plugin "{name}"')

        spec = importlib.util.spec_from_file_location(f'aj.plugins.{name}',f'{info["path"]}/__init__.py')
        module = importlib.util.module_from_spec(spec)
        sys.modules[f'{spec.name}'] = module
        info['module'] = module

        spec.loader.exec_module(module)

        info['imported'] = True

    def __init_plugin_module(self, name, info):
        logging.debug(f'Initializing plugin "{name}"')
        mod = info['module']
        if hasattr(mod, 'init'):
            mod.init(self)
        info['initialized'] = True
