from ajenti.api import plugin
from ajenti.plugins.dashboard.api import ConfigurableWidget
from ajenti.ui import on

from api import ServiceMultiplexor


@plugin
class ServiceWidget (ConfigurableWidget):
    name = _('Service')
    icon = 'play'

    def on_prepare(self):
        self.mgr = ServiceMultiplexor.get()
        self.append(self.ui.inflate('services:widget'))

    def on_start(self):
        self.service = self.mgr.get_one(self.config['service'])
        if not self.service:
            return
        self.find('name').text = self.service.name
        self.find('icon').icon = self.service.icon
        self.find('start').visible = not self.service.running
        self.find('stop').visible = self.service.running
        self.find('restart').visible = self.service.running

    def create_config(self):
        return {'service': ''}

    def on_config_start(self):
        service_list = self.dialog.find('service')
        service_list.labels = service_list.values = [x.name for x in self.mgr.get_all()]
        service_list.value = self.config['service']

    def on_config_save(self):
        self.config['service'] = self.dialog.find('service').value

    @on('start', 'click')
    def on_s_start(self):
        self.service.start()
        self.on_start()

    @on('restart', 'click')
    def on_s_restart(self):
        self.service.restart()
        self.on_start()

    @on('stop', 'click')
    def on_s_stop(self):
        self.service.stop()
        self.on_start()
