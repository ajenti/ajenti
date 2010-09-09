import os
import imp
import sys

loaded_plugins = []

class PluginRequirementError (Exception):
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return 'Plugin \'%s\' required' % self.name
        
    
def require(name):
    global loaded_plugins
    if not name.lower() in loaded_plugins:
        raise PluginRequirementError(name)
    
    
def loader(path, log):
    global loaded_plugins
    
    plugs = [plug for plug in os.listdir(path) if not plug.startswith('.')]
    plugs = [plug[:-3] if plug.endswith('.py') else plug for plug in plugs]
    plugs = list(set(plugs)) # Leave just unique items
    plugs_found = {}
    plugs_names = []
    for plug in plugs:
        try:
            p = imp.find_module(plug, [path])
            plugs_found[plug] = p
            plugs_names.append(plug)
        except ImportError:
            pass

    queue = plugs_names
    retries = {}
    
    while len(queue) > 0:
        c = queue[-1]
        if not retries.has_key(c):
            retries[c] = 0
            
        p = plugs_found[c]
        try:
            imp.load_module(c, p[0], p[1], p[2])
            queue.remove(c)
            loaded_plugins.append(c.lower())
            log.debug('Loaded plugin %s' % c)
        except PluginRequirementError, e:
            retries[c] += 1
            if retries[c] > 10:
                log.error('Circular dependency between %s and %s. Aborting' % (c,e.name))
                sys.exit(1)
            queue.remove(e.name)
            queue.append(e.name)
