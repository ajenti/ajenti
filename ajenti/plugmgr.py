import os
import imp
import sys
import traceback

from ajenti.com import *
from ajenti.utils import detect_platform, shell, shell_status, download
from ajenti.feedback import *


RETRY_LIMIT = 10
loaded_plugins = []
plugin_info = {}
loaded_mods = {}
disabled_plugins = {}


class BaseRequirementError(Exception):
    pass
    
    
class PluginRequirementError(BaseRequirementError):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return 'requires plugin %s' % self.name


class SoftwareRequirementError(BaseRequirementError):
    def __init__(self, name, bin):
        self.name = name
        self.bin = bin
    
    def __str__(self):
        return 'requires %s (%s)' % (self.name, self.bin)


class PluginInstaller(Plugin):
    def __init__(self):
        self.server = self.app.config.get('ajenti', 'update_server')
        self.available = []
        try:
            data = open('/var/lib/ajenti/plugins.list').read()
            self.available = eval(data)
        except:
            pass
            
    def list_plugins(self):
        res = []
        dir = self.app.config.get('ajenti', 'plugins')

        for k in disabled_plugins.keys():
            i = PluginInfo()
            i.id = k
            i.icon = '/dl/%s/icon.png'%k
            i.name, i.desc, i.version = k, 'Disabled', ''
            i.problem = str(disabled_plugins[k])
            i.author, i.homepage = '', ''
            res.append(i)

        res.extend(plugin_info.values())
        
        return sorted(res, key=lambda x:x.name)
        
    def update_list(self):        
        if not os.path.exists('/var/lib/ajenti'):
            os.mkdir('/var/lib/ajenti')
        send_stats(self.server)
        data = download('http://%s/plugins.php' % self.server)
        try:
            open('/var/lib/ajenti/plugins.list', 'w').write(data)
            self.available = eval(data)
        except:
            pass
        self.available = eval(data)

    def remove(self, id):        
        dir = self.app.config.get('ajenti', 'plugins')
        send_stats(self.server, delplugin=id)
        shell('rm -r %s/%s' % (dir, id))

    def install(self, id):        
        dir = self.app.config.get('ajenti', 'plugins')
        self.remove(id)
                
        download('http://%s/plugins/%s/plugin.tar.gz' % (self.server, id), 
            file='%s/plugin.tar.gz'%dir, crit=True)
            
        shell('cd %s; tar -xf plugin.tar.gz' % dir)
        shell('rm %s/plugin.tar.gz' % dir)
        send_stats(self.server, addplugin=id)
        load_plugin(self.app.config.get('ajenti', 'plugins'), id, self.log, self.app.platform)
    
    def install_file(self, stream):        
        dir = self.app.config.get('ajenti', 'plugins')
        self.remove(id)
                
        open('%s/plugin.tar.gz'%dir, 'w').write(stream)
            
        shell('cd %s; tar -xf plugin.tar.gz' % dir)
        shell('rm %s/plugin.tar.gz' % dir)
    

class PluginInfo:
    pass    
    
            
def get_deps(platform, dep):
    d = []
    for k in dep:
        if platform.lower() in k[0] or 'any' in k[0]:
            d.extend(k[1])
    return d
        
def verify_dep(dep):
    if dep[0] == 'app':
        return shell_status('which '+dep[2])==0
    if dep[0] == 'plugin':
        return dep[1] in loaded_plugins
        
def get_plugin_path(app, id):
    if id in loaded_plugins:
        return app.config.get('ajenti', 'plugins')
    else:
        return os.path.join(os.path.split(__file__)[0], 'plugins') # ./plugins
        
def load_plugin(path, plugin, log, platform):
    try:
        log.debug('Loading plugin %s' % plugin)
        mod = imp.load_module(plugin, *imp.find_module(plugin, [path]))
        loaded_mods[plugin] = mod
            
        # Verify dependencies
        if hasattr(mod, 'DEPS'):
            for req in get_deps(platform, mod.DEPS):
                if not verify_dep(req):
                    if req[0] == 'plugin':
                        raise PluginRequirementError(req[1])
                    if req[0] == 'app':
                        raise SoftwareRequirementError(*req[1:])
           
        # Load submodules
        if not hasattr(mod, 'MODULES'):
            log.error('Plugin %s doesn\'t have correct metainfo. Aborting' % plugin)
            sys.exit(1)
        for submod in mod.MODULES:
            description = imp.find_module(submod, mod.__path__)
            try:
                imp.load_module(plugin + '.' + submod, *description)
                log.debug('Loaded submodule %s.%s' % (plugin,submod))
            except Exception, e:
                print traceback.format_exc()
                log.warn('Skipping submodule %s.%s (%s)'%(plugin,submod,str(e)))
                    
        # Save info
        i = PluginInfo()
        i.id = plugin
        i.icon = '/dl/%s/icon.png'%plugin
        i.name, i.desc, i.version = mod.NAME, mod.DESCRIPTION, mod.VERSION
        i.author, i.homepage = mod.AUTHOR, mod.HOMEPAGE
        i.problem = None
        plugin_info[plugin] = i
        loaded_plugins.append(plugin)
    except BaseRequirementError, e:
        raise e
    except Exception, e:
        disabled_plugins[plugin] = e
        log.warn('Plugin %s disabled (%s)' % (plugin, str(e)))
        print traceback.format_exc()
        raise e        
        
def load_plugins(path, log):
    global loaded_plugins
    
    plugs = [plug for plug in os.listdir(path) if not plug.startswith('.')]
    plugs = [plug[:-3] if plug.endswith('.py') else plug for plug in plugs]
    plugs = list(set(plugs)) # Leave just unique items

    queue = plugs
    retries = {}
    platform = detect_platform()
    log.info('Detected platform: %s'%platform)
    
    while len(queue) > 0:
        plugin = queue[-1]
        if not plugin in retries:
            retries[plugin] = 0
            
        try:
            load_plugin(path, plugin, log, platform) 
            queue.remove(plugin)
        except PluginRequirementError, e:
            retries[plugin] += 1
            if retries[plugin] > RETRY_LIMIT:
                log.error('Circular dependency between %s and %s. Aborting' % (plugin,e.name))
                sys.exit(1)
            try:
                queue.remove(e.name)
                queue.append(e.name)
                if e.name in disabled_plugins:
                    raise e
            except:
                log.warn('Plugin %s requires plugin %s, which is not available.' % (plugin,e.name))
                disabled_plugins[plugin] = e
                queue.remove(plugin)
        except SoftwareRequirementError, e:
            log.warn('Plugin %s requires application %s (%s), which is not available.' % (plugin,e.name,e.bin))
            disabled_plugins[plugin] = e
            queue.remove(plugin)
        except Exception, e:
            queue.remove(plugin)

    log.info('Plugins loaded.')
