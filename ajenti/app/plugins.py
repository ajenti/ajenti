import os
import imp
import sys

from ajenti.requirements import *


RETRY_LIMIT = 10
loaded_plugins = []
disabled_plugins = {}


def loader(path, log):
    global loaded_plugins
    
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
            log.debug('Loading plugin %s' % plugin)
            mod = imp.load_module(plugin, *imp.find_module(plugin, [path]))
            if hasattr(mod, 'REQUIRE'):
                for req in mod.REQUIRE:
                    req.test(loaded_plugins)
            if not hasattr(mod, 'MODULES'):
                log.error('Plugin %s doesn\'t have correct metainfo. Aborting' % plugin)
                sys.exit(1)
            for submod in mod.MODULES:
                description = imp.find_module(submod, mod.__path__)
                imp.load_module(plugin + '.' + submod, *description)
                log.debug('Loaded submodule %s.%s' % (plugin,submod))
            queue.remove(plugin)
            loaded_plugins.append(plugin)
        except PluginRequirement, e:
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
                log.warn('Plugin %s requires %s, which is not available.' % (plugin,e.name))
                disabled_plugins[plugin] = e
                queue.remove(plugin)
        except Exception, e:
            disabled_plugins[plugin] = e
            log.warn('Plugin %s disabled (%s)' % (plugin, str(e)))
            queue.remove(plugin)
    log.info('Plugins loaded.')
                
