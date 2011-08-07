from ajenti.api import *
from ajenti import apis


class ServiceMeter (BinaryMeter):
    name = 'Services'
    category = 'Software'

    def get_variants(self):
        return [x.name for x in self.app.get_backend(apis.services.IServiceManager).list_all()]

    def init(self):
        self.mgr = self.app.get_backend(apis.services.IServiceManager)
        self.text = self.variant

    def get_value(self):
        return self.mgr.get_status(self.variant) == 'running'
