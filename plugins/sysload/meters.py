from ajenti.api import *


class SysloadMeter (DecimalMeter):
    name = 'System load'
    category = 'System'
    transform = 'float'

    def get_variants(self):
        return ['1', '5', '15']

    def init(self):
        self.load = self.app.get_backend(apis.sysstat.ISysStat).get_load()
        self.text = self.variant + ' min'

    def get_value(self):
        return float(self.load[self.get_variants().index(self.variant)])


class RAMMeter (LinearMeter):
    name = 'RAM'
    category = 'System'
    transform = 'fsize_percent'

    def init(self):
        self.ram = self.app.get_backend(apis.sysstat.ISysStat).get_ram()

    def get_max(self):
        return int(self.ram[1])

    def get_value(self):
        return int(self.ram[0])


class SwapMeter (LinearMeter):
    name = 'Swap'
    category = 'System'
    transform = 'fsize_percent'

    def init(self):
        self.swap = self.app.get_backend(apis.sysstat.ISysStat).get_swap()

    def get_max(self):
        return int(self.swap[1])

    def get_value(self):
        return int(self.swap[0])
