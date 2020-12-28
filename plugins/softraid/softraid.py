class RAIDDevice():
    """
    Basic class to store raid devices details.
    """

    def __init__(self):
        self.name = ''
        self.up = False
        self.failed = False
        self.spared = False
        self.down = False
        self.index = 0


class RAIDArray():
    """
    Basic class to store raid arrays details.
    """

    def __init__(self):
        self.name = ''
        self.type = ''
        self.state = ''
        self.active = ''
        self.blocks = 0
        self.chunk = 0
        self.size = 0
        self.superblock = ''
        self.devices = []
        self.devices_down = 0
        self.recovery = False
        self.recovery_progress = 0
        self.recovery_remaining = ''
        self.recovery_speed = ''

class RAIDManager():
    """
    Global object to parse raid arrays and devices from /proc/mdstat.
    """

    def __init__(self):
        self.refresh()

    def refresh(self):
        """
        Update the self.arrays list of arrays through parsing the /proc/mdstat
        file, and store RAIDArray and RAIDdevices objects.
        """

        self.arrays = []
        with open('/proc/mdstat') as f:
            ll = f.read().splitlines()
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
                array.size = round(array.blocks / 1024 / 1024, 2)
                array.superblock = tokens[3]
                if 'chunk' in l:
                    array.chunk = tokens[6]

                array.devices_down = tokens[-1][1:-1].count("_")

                self.arrays.append(array.__dict__)

                for device_str in devices:
                    device = RAIDDevice()
                    device.name = device_str.split('[')[0]
                    device.index = int(device_str.split('[')[1].split(']')[0])
                    if device_str.endswith("(F)"):
                        device.failed = True
                    elif device_str.endswith("(S)"):
                        device.spared = True
                    else:
                        device.up = True
                    array.devices.append(device.__dict__)

                l = ll.pop(0)
                if 'recovery' in l:
                    array.recovery = True
                    array.recovery_progress = float(l.split()[3].strip('%'))
                    array.recovery_remaining = l.split()[5].split('=')[1]
                    array.recovery_speed = l.split()[6].split('=')[1]