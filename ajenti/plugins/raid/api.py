from ajenti.api import *


class RAIDDevice (object):
    def __init__(self):
        self.name = ''
        self.up = False
        self.failed = False
        self.spared = False
        self.index = 0


class RAIDArray (object):
    def __init__(self):
        self.name = ''
        self.type = ''
        self.blocks = 0
        self.metadata = ''
        self.devices = []
        self.recovery = False
        self.recovery_progress = 0
        self.recovery_remaining = ''


@plugin
class RAIDManager (BasePlugin):
    def __init__(self):
        self.refresh()

    def refresh(self):
        self.arrays = []
        ll = open('/proc/mdstat').read().splitlines()
        while ll:
            l = ll.pop(0)
            if l.startswith('Personalities'):
                continue
            if l.startswith('unused'):
                continue
            if ':' in l:
                array = RAIDArray()
                array.name, tokens = l.split(':')
                array.name = array.name.strip()
                tokens = tokens.split()

                if tokens[1].startswith('('):
                    tokens[0] += ' ' + tokens[1]
                    tokens.pop(1)

                array.state = tokens[0]
                array.active = array.state == 'active'
                array.type = tokens[1]
                devices = tokens[2:]

                l = ll.pop(0)
                tokens = l.split()
                array.blocks = int(tokens[0])
                array.metadata = tokens[3]

                states = tokens[-1][1:-1]

                self.arrays.append(array)

                for i, device_str in enumerate(devices):
                    device = RAIDDevice()
                    device.name = device_str.split('[')[0]
                    device.index = int(device_str.split('[')[1].split(']')[0])
                    if device_str.endswith("(F)"):
                        device.failed = True
                    elif device_str.endswith("(S)"):
                        device.spared = True
                    else:
                        device.up = True
                    array.devices.append(device)                

                l = ll.pop(0)
                if 'recovery' in l:
                    array.recovery = True
                    array.recovery_progress = float(l.split()[3].strip('%')) / 100
                    array.recovery_remaining = l.split()[5].split('=')[1]
