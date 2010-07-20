import os
import imp
import sys


def loader(path):
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

    for plug in sorted(plugs_names):
        p = plugs_found[plug]
        imp.load_module(plug, p[0], p[1], p[2])

