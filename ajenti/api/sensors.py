import time

from ajenti.api import *


@interface
class Sensor (object):
    id = None
    timeout = 0

    def init(self):
        self.cache = {}
        self.last_measurement = {}

    @staticmethod
    def find(id):
        for cls in Sensor.get_classes():
            if cls.id == id:
                return cls.get()
        else:
            return None

    def value(self, variant=None):
        t = time.time()
        if (not variant in self.cache) or (t - self.last_measurement[variant]) > self.timeout:
            self.cache[variant] = self.measure(variant)
            self.last_measurement[variant] = t
        return self.cache[variant]

    def get_variants(self):
        return [None]

    def measure(self, variant=None):
        pass
