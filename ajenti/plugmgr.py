"""
Tools for manipulating plugins and repository
"""

__all__ = [
    'BaseRequirementError',
    'PlatformRequirementError',
    'PluginRequirementError',
    'ModuleRequirementError',
    'SoftwareRequirementError',
    'PluginLoader',
    'RepositoryManager',
    'PluginInfo',
]

import os
import imp
import sys
import traceback
import weakref

from ajenti.com import *
from ajenti.utils import detect_platform, shell, shell_status, download
from ajenti.feedback import *
from ajenti import generation
import ajenti

RETRY_LIMIT = 10


class BaseRequirementError(Exception):
    """
    Basic exception that means a plugin wasn't loaded due to unmet
    dependencies
    """


class PlatformRequirementError(BaseRequirementError):
    """
    Exception that means a plugin wasn't loaded due to
    unsupported platform
    """

    def __init__(self, lst):
        self.lst = lst

    def __str__(self):
        return 'requires platforms %s' % self.lst


class PluginRequirementError(BaseRequirementError):
    """
    Exception that means a plugin wasn't loaded due to
    required plugin being unavailable
    """

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return 'requires plugin "%s"' % self.name


class ModuleRequirementError(BaseRequirementError):
    """
    Exception that means a plugin wasn't loaded due to
    required Python module being unavailable
    """

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return 'requires Python module "%s"' % self.name


class SoftwareRequirementError(BaseRequirementError):
    """
    Exception that means a plugin wasn't loaded due to
    required software being unavailable
    """

    def __init__(self, name, bin):
        self.name = name
        self.bin = bin

    def __str__(self):
        return 'requires application "%s" (executable: %s)' % (self.name, self.bin)


class PluginLoader:
    """
    Handles plugin loading and unloading
    """

    __classes = {}
    __plugins = {}
    __submods = {}
    __managers = []
    __observers = []
    platform = None
    log = None
    path = None

    @staticmethod
    def initialize(log, path, platform):
        """
        Initializes the PluginLoader

        :param  log:        Logger
        :type   log:        :class:`logging.Logger`
        :param  path:       Path to the plugins
        :type   path:       str
        :param  platform:   System platform for plugin validation
        :type   platform:   str
        """

        PluginLoader.log = log
        PluginLoader.path = path
        PluginLoader.platform = platform

    @staticmethod
    def list_plugins():
        """
        Returns dict of :class:`PluginInfo` for all plugins
        """

        return PluginLoader.__plugins

    @staticmethod
    def register_mgr(mgr):
        """
        Registers an :class:`ajenti.com.PluginManager` from which the unloaded
        classes will be removed when a plugin is unloaded
        """
        PluginLoader.__managers.append(mgr)

    @staticmethod
    def register_observer(mgr):
        """
        Registers an observer which will be notified when plugin set is changed.
        Observer should have a callable ``plugins_changed`` method.
        """
        PluginLoader.__observers.append(weakref.ref(mgr, \
            callback=PluginLoader.__unregister_observer))

    @staticmethod
    def __unregister_observer(ref):
        PluginLoader.__observers.remove(ref)

    @staticmethod
    def notify_plugins_changed():
        """
        Notifies all observers that plugin set has changed.
        """
        for o in PluginLoader.__observers:
            if o():
                o().plugins_changed()

    @staticmethod
    def load(plugin):
        """
        Loads given plugin
        """
        log = PluginLoader.log
        path = PluginLoader.path
        platform = PluginLoader.platform

        log.debug('Loading plugin %s' % plugin)
        try:
            mod = imp.load_module(plugin, *imp.find_module(plugin, [path]))
        except:
            log.warn(' *** Plugin not loadable: ' + plugin)
            return

        try:
            # Save info
            info = PluginInfo()
            info.id = plugin
            info.icon = '/dl/%s/icon.png'%plugin
            info.name, info.desc, info.version = mod.NAME, mod.DESCRIPTION, mod.VERSION
            info.author, info.homepage = mod.AUTHOR, mod.HOMEPAGE
            info.deps = []
            info.problem = None
            info.installed = True
            info.descriptor = mod

            PluginLoader.__plugins[plugin] = info

            # Verify platform
            if mod.PLATFORMS != ['any'] and not platform in mod.PLATFORMS:
                raise PlatformRequirementError(mod.PLATFORMS)

            # Verify dependencies
            if hasattr(mod, 'DEPS'):
                deps = []
                for k in mod.DEPS:
                    if platform.lower() in k[0] or 'any' in k[0]:
                        deps = k[1]
                        break
                info.deps = deps
                for req in deps:
                    PluginLoader.verify_dep(req)

            PluginLoader.__classes[plugin] = []
            PluginLoader.__submods[plugin] = {}

            # Load submodules
            for submod in mod.MODULES:
                try:
                    log.debug('  -> %s' % submod)
                    PluginManager.start_tracking()
                    m = imp.load_module(plugin + '.' + submod, *imp.find_module(submod, mod.__path__))
                    classes = PluginManager.stop_tracking()
                    # Record new Plugin subclasses
                    PluginLoader.__classes[plugin] += classes
                    # Store submodule
                    PluginLoader.__submods[plugin][submod] = m
                    setattr(mod, submod, m)
                except ImportError, e:
                    del mod
                    raise ModuleRequirementError(e.message.split()[-1])
                except Exception, e:
                    del mod
                    raise

            # Store the whole plugin
            setattr(ajenti.plugins, plugin, mod)
            PluginLoader.notify_plugins_changed()
        except BaseRequirementError, e:
            info.problem = e
            raise e
        except Exception, e:
            log.warn(' *** Plugin loading failed: %s' % str(e))
            print traceback.format_exc()
            PluginLoader.unload(plugin)
            info.problem = e
            raise e

    @staticmethod
    def load_plugins():
        """
        Loads all plugins from plugin path
        """
        log = PluginLoader.log
        path = PluginLoader.path

        plugs = [plug for plug in os.listdir(path) if not plug.startswith('.')]
        plugs = [plug[:-3] if plug.endswith('.py') else plug for plug in plugs]
        plugs = list(set(plugs)) # Leave just unique items

        queue = plugs
        retries = {}

        while len(queue) > 0:
            plugin = queue[-1]
            if not plugin in retries:
                retries[plugin] = 0

            try:
                PluginLoader.load(plugin)
                queue.remove(plugin)
            except PluginRequirementError, e:
                retries[plugin] += 1
                if retries[plugin] > RETRY_LIMIT:
                    log.error('Circular dependency between %s and %s. Aborting' % (plugin,e.name))
                    sys.exit(1)
                try:
                    queue.remove(e.name)
                    queue.append(e.name)
                    if (e.name in PluginLoader.__plugins) and (PluginLoader.__plugins[e.name].problem is not None):
                        raise e
                except:
                    log.warn('Plugin %s requires plugin %s, which is not available.' % (plugin,e.name))
                    queue.remove(plugin)
            except BaseRequirementError, e:
                log.warn('Plugin %s %s' % (plugin,str(e)))
                PluginLoader.unload(plugin)
                queue.remove(plugin)
            except Exception, e:
                PluginLoader.unload(plugin)
                queue.remove(plugin)
                raise
        log.info('Plugins loaded.')

    @staticmethod
    def unload(plugin):
        """
        Unloads given plugin
        """
        PluginLoader.log.info('Unloading plugin %s'%plugin)
        if plugin in PluginLoader.__classes:
            for cls in PluginLoader.__classes[plugin]:
                for m in PluginLoader.__managers:
                    i = m.instance_get(cls)
                    if i is not None:
                        i.unload()
                PluginManager.class_unregister(cls)
        if plugin in PluginLoader.__submods:
            del PluginLoader.__submods[plugin]
        if plugin in PluginLoader.__classes:
            del PluginLoader.__classes[plugin]
        PluginLoader.notify_plugins_changed()

    @staticmethod
    def verify_dep(dep):
        """
        Verifies that given plugin dependency is satisfied. Returns bool
        """
        if dep[0] == 'app':
            if shell_status('which '+dep[2]) != 0:
                raise SoftwareRequirementError(*dep[1:])
        if dep[0] == 'plugin':
            if not dep[1] in PluginLoader.list_plugins() or \
                    PluginLoader.__plugins[dep[1]].problem:
                raise PluginRequirementError(*dep[1:])
        if dep[0] == 'module':
            try:
                exec('import %s'%dep[1])
            except:
                raise ModuleRequirementError(*dep[1:])

    @staticmethod
    def get_plugin_path(app, id):
        """
        Returns path for plugin's files. Parameters: :class:`ajenti.core.Application`, ``str``
        """
        if id in PluginLoader.list_plugins():
            return app.config.get('ajenti', 'plugins')
        else:
            return os.path.join(os.path.split(__file__)[0], 'plugins') # ./plugins


class RepositoryManager:
    """
    Manages official Ajenti plugin repository. ``cfg`` is :class:`ajenti.config.Config`

    - ``available`` - list(:class:`PluginInfo`), plugins available in the repository
    - ``installed`` - list(:class:`PluginInfo`), plugins that are locally installed
    - ``upgradable`` - list(:class:`PluginInfo`), plugins that are locally installed
      and have other version in the repository
    """

    def __init__(self, cfg):
        self.config = cfg
        self.server = cfg.get('ajenti', 'update_server')
        self.refresh()

    def refresh(self):
        """
        Re-reads saved repository information and rebuilds installed/available lists
        """
        self.available = []
        self.installed = []
        self.update_installed()
        self.update_available()
        self.update_upgradable()

    def update_available(self):
        """
        Re-reads saved list of available plugins
        """
        try:
            data = eval(open('/var/lib/ajenti/plugins.list').read())
        except:
            return
        self.available = []
        for item in data:
            inst = False
            for i in self.installed:
                if i.id == item['id'] and i.version == item['version']:
                    inst = True
                    break
            if inst:
                continue

            i = PluginInfo()
            for k,v in item.items():
                setattr(i, k, v)
            i.installed = False
            i.problem = None
            self.available.append(i)

    def update_installed(self):
        """
        Rebuilds list of installed plugins
        """
        self.installed = sorted(PluginLoader.list_plugins().values(), key=lambda x:x.name)

    def update_upgradable(self):
        """
        Rebuilds list of upgradable plugins
        """
        upg = []
        for p in self.available:
            u = False
            for g in self.installed:
                if g.id == p.id and g.version != p.version:
                    u = True
                    break
            if u:
                g.upgradable = p.upgradable = True
                upg += [g]
        self.upgradable = upg

    def update_list(self):
        """
        Downloads fresh list of plugins and rebuilds installed/available lists
        """
        if not os.path.exists('/var/lib/ajenti'):
            os.mkdir('/var/lib/ajenti')
        send_stats(self.server, PluginLoader.list_plugins().keys())
        data = download('http://%s/api/plugins?pl=%s&gen=%s' % (self.server,detect_platform(),generation))
        try:
            open('/var/lib/ajenti/plugins.list', 'w').write(data)
        except:
            pass
        self.update_installed()
        self.update_available()
        self.update_upgradable()

    def remove(self, id):
        """
        Uninstalls given plugin

        :param  id:     Plugin id
        :type   id:     str
        """
        dir = self.config.get('ajenti', 'plugins')
        send_stats(self.server, PluginLoader.list_plugins().keys(), delplugin=id)
        shell('rm -r %s/%s' % (dir, id))

        if id in PluginLoader.list_plugins():
            PluginLoader.unload(id)

        self.update_installed()
        self.update_available()

    def install(self, id, load=True):
        """
        Installs a plugin

        :param  id:     Plugin id
        :type   id:     str
        :param  load:   True if you want Ajenti to load the plugin immediately
        :type   load:   bool
        """
        dir = self.config.get('ajenti', 'plugins')

        download('http://%s/plugins/%s/%s/plugin.tar.gz' % (self.server, generation, id),
            file='%s/plugin.tar.gz'%dir, crit=True)

        self.remove(id)
        self.install_tar(load=load)

    def install_stream(self, stream):
        """
        Installs a plugin from a stream containing the package

        :param  stream: Data stream
        :type   stream: file
        """
        dir = self.config.get('ajenti', 'plugins')
        open('%s/plugin.tar.gz'%dir, 'w').write(stream)
        self.install_tar()

    def install_tar(self, load=True):
        """
        Unpacks and installs a ``plugin.tar.gz`` file located in the plugins directory.

        :param  load:   True if you want Ajenti to load the plugin immediately
        :type   load:   bool
        """
        dir = self.config.get('ajenti', 'plugins')

        id = shell('tar tzf %s/plugin.tar.gz'%dir).split('\n')[0].strip('/')

        shell('cd %s; tar -xf plugin.tar.gz' % dir)
        shell('rm %s/plugin.tar.gz' % dir)

        send_stats(self.server, PluginLoader.list_plugins().keys(), addplugin=id)

        if load:
            PluginLoader.load(id)

        self.update_installed()
        self.update_available()
        self.update_upgradable()


class PluginInfo:
    """
    Container for the plugin description
    - ``upgradable`` - `bool`, if the plugin can be upgraded
    - ``problem``- :class:`Exception` which occured while loading plugin, else ``None``
    - ``deps`` - list of dependency tuples
    And other fields read by :class:`PluginLoader` from plugin's ``__init__.py``
    """

    def __init__(self):
        self.upgradable = False
        self.problem = None
        self.deps = []

    def str_req(self):
        """
        Formats plugin's unmet requirements into human-readable string

        :returns:    str
        """

        reqs = []
        for p in self.deps:
            if any(x in [PluginLoader.platform, 'any'] for x in p[0]):
                for r in p[1]:
                    try:
                        PluginLoader.verify_dep(r)
                    except Exception, e:
                        reqs.append(str(e))
        return ', '.join(reqs)
