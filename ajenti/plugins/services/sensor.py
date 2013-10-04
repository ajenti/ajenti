from ajenti.api import plugin
from ajenti.api.sensors import Sensor
from api import ServiceMultiplexor


@plugin
class ServiceSensor (Sensor):
    id = 'service'
    timeout = 5

    def init(self):
        self.sm = ServiceMultiplexor.get()

    def get_variants(self):
        return [x.name for x in self.sm.get_all()]

    def measure(self, variant):
        s = self.sm.get_one(variant)
        if not s:
            return 0
        return int(s.running)
