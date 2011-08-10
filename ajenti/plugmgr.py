import os
import imp
import sys
import traceback

from ajenti.com import *
from ajenti.utils import detect_platform, shell, shell_status, download
from ajenti.feedback import *
from ajenti import generation

RETRY_LIMIT = 10


class BaseRequirementError(Exception):
    pass


class PlatformRequirementError(BaseRequirementError):
    def __init__(self, lst):
        self.lst = lst

    def __str__(self):
        return 'requires platforms %s' % self.lst


class PluginRequirementError(BaseRequirementError):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return 'requires plugin %s' % self.name


class ModuleRequirementError(BaseRequirementError):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return 'requires Python module %s' % self.name


class SoftwareRequirementError(BaseRequirementError):
    def __init__(self, name, bin):
        self.name = name
        self.bin = bin

    def __str__(self):
        return 'requires application %s (%s)' % (self.name, self.bin)


class PluginLoader:
    __classes = {}
    __plugins = {}
    __submods = {}
    __managers = []
    platform = None
    log = None
    path = None

    @staticmethod
    def initialize(log, path, platform):
        PluginLoader.log = log
        PluginLoader.path = path
        PluginLoader.platform = platform

    @staticmethod
    def list_plugins():
        return PluginLoader.__plugins

    @staticmethod
    def register_mgr(mgr):
        PluginLoader.__managers.append(mgr)

    @staticmethod
    def load(plugin):
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
                except Exception, e:
                    del mod
                    raise

            # Store the whole plugin
            setattr(ajenti.plugins, plugin, mod)
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
                queue.remove(plugin)
            except Exception, e:
                queue.remove(plugin)
                raise
        log.info('Plugins loaded.')

    @staticmethod
    def unload(plugin):
        for cls in PluginLoader.__classes[plugin]:
            for m in PluginLoader.__managers:
                i = m.instance_get(cls)
                if i is not None:
                    i.unload()
            PluginManager.class_unregister(cls)
        del PluginLoader.__plugins[plugin]
        del PluginLoader.__submods[plugin]
        del PluginLoader.__classes[plugin]

    @staticmethod
    def verify_dep(dep):
        if dep[0] == 'app':
            if shell_status('which '+dep[2]) != 0:
                raise SoftwareRequirementError(*dep[1:])
        if dep[0] == 'plugin':
            if not dep[1] in PluginLoader.list_plugins():
                raise PluginRequirementError(*dep[1:])
        if dep[0] == 'module':
            try:
                exec('import %s'%dep[1])
            except:
                raise ModuleRequirementError(*dep[1:])

    @staticmethod
    def get_plugin_path(app, id):
        if id in PluginLoader.list_plugins():
            return app.config.get('ajenti', 'plugins')
        else:
            return os.path.join(os.path.split(__file__)[0], 'plugins') # ./plugins


class RepositoryManager:
    def __init__(self, cfg):
        self.config = cfg
        self.server = cfg.get('ajenti', 'update_server')
        self.available = []
        self.installed = []
        self.update_installed()
        self.update_available()
        self.update_upgradable()

    def update_available(self):
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
        self.installed = sorted(PluginLoader.list_plugins().values(), key=lambda x:x.name)

    def update_upgradable(self):
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
        dir = self.config.get('ajenti', 'plugins')
        send_stats(self.server, PluginLoader.list_plugins().keys(), delplugin=id)
        shell('rm -r %s/%s' % (dir, id))

        if id in PluginLoader.list_plugins():
            PluginLoader.unload(id)

        self.update_installed()
        self.update_available()

    def install(self, id, load=True):
        dir = self.config.get('ajenti', 'plugins')

        download('http://%s/plugins/%s/%s/plugin.tar.gz' % (self.server, generation, id),
            file='%s/plugin.tar.gz'%dir, crit=True)

        self.remove(id)
        self.install_tar(load=load)

    def install_stream(self, stream):
        dir = self.config.get('ajenti', 'plugins')
        open('%s/plugin.tar.gz'%dir, 'w').write(stream)
        self.install_tar()

    def install_tar(self, load=True):
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
    def __init__(self):
        self.upgradable = False
        self.problem = None
        self.deps = []

    def str_req(self):
        reqs = []
        for r in self.deps:
            try:
                PluginLoader.verify_dep(r)
            except Exception, e:
                reqs.append(str(e))
        return ', '.join(reqs)
