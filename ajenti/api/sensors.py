import time

from ajenti.api import *


@interface
@persistent
class Sensor (object):
    """
    Base class for a Sensor. Sensors measure system status parameters and can be queried from other plugins.
    """
    id = None
    timeout = 0

    def init(self):
        self.cache = {}
        self.last_measurement = {}

    @staticmethod
    def find(id):
        """
        Returns a Sensor by name

        :param id: sensor ID
        :type  id: str
        :rtype: :class:`Sensor`, None
        """
        for cls in Sensor.get_classes():
            if cls.id == id:
                return cls.get()
        else:
            return None

    def value(self, variant=None):
        """
        Returns sensor's measurement for a specific `variant`. Sensors can have multiple variants; for example, disk usage sensor accepts device name as a variant.

        :param variant: variant to measure
        :type  variant: str, None
        :rtype: int, float, tuple, list, dict, str
        """
        t = time.time()
        if (not variant in self.cache) or (t - self.last_measurement[variant]) > self.timeout:
            self.cache[variant] = self.measure(variant)
            self.last_measurement[variant] = t
        return self.cache[variant]

    def get_variants(self):
        """
        Override this and return a list of available variants.

        :rtype: list
        """
        return [None]

    def measure(self, variant=None):
        """
        Override this and perform the measurement.

        :param variant: variant to measure
        :type  variant: str, None
        :rtype: int, float, tuple, list, dict, str
        """
