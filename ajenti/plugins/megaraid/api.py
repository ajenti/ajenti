import subprocess
from ajenti.api import *


class RAIDDevice (object):
    def __init__(self):
        self.name = ''
        self.up = False
        self.failed = False
        self.index = 0


class RAIDArray (object):
    def __init__(self):
        self.id = ''
        self.name = ''
        self.level = ''
        self.size = 0
        self.state = ''
        self.disks = []


class RAIDAdapter (object):
    def __init__(self):
        self.id = ''
        self.name = ''
        self.arrays = []


@plugin
class RAIDManager (BasePlugin):
    cli_path = '/opt/MegaRAID/MegaCli/MegaCli'

    def __init__(self):
        self.refresh()

    def refresh(self):
        self.adapters = []

        ll = subprocess.check_output([self.cli_path, '-LDPDInfo', '-aall']).splitlines()
        #ll = open('mraid.txt').read().splitlines()
        current_adapter = None
        current_array = None
        current_disk = None
        while ll:
            l = ll.pop(0)
            if l.startswith('Adapter'):
                current_adapter = RAIDAdapter()
                self.adapters.append(current_adapter)
                current_array = None
                current_disk = None
                current_adapter.id = l.split('#')[1].strip()
                continue
            if l.startswith('Virtual Drive'):
                current_array = RAIDArray()
                current_adapter.arrays.append(current_array)
                current_disk = None
                current_array.id = l.split()[2]
                continue
            if l.startswith('PD:'):
                current_disk = RAIDDevice()
                current_array.disks.append(current_disk)
                current_disk.id = l.split()[1]
            if ':' in l:
                k, v = l.split(':', 1)
                k = k.strip().lower().replace(' ', '_')
                v = v.strip()
                o = current_disk or current_array or current_adapter
                setattr(o, k, v)

    def find_array(self, name):
        for a in self.adapters:
            for arr in a.arrays:
                if arr.name == name:
                    return arr

    def list_arrays(self):
        for a in self.adapters:
            for arr in a.arrays:
                yield arr.name
