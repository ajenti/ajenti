import os
import imp
import sys


def loader(path):
    plugs = [plug for plug in os.listdir(path) if not plug.startswith('.')]
    plugs = [plug[:-3] if plug.endswith('.py') else plug for plug in plugs]
    plugs = sorted(list(set(plugs))) # Leave just unique items
    plugs_found = {}
    for plug in plugs:
        try:
            p = imp.find_module(plug, [path])
            plugs_found[plug] = p
        except ImportError:
            pass
    for plug in plugs_found:
        p = plugs_found[plug]
        imp.load_module(plug, p[0], p[1], p[2])

