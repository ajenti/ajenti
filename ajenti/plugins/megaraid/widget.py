from ajenti.api import plugin
from ajenti.plugins.dashboard.api import ConfigurableWidget

from api import RAIDManager


@plugin
class LSIWidget (ConfigurableWidget):
    name = 'LSI MegaRAID'
    icon = 'hdd'

    def on_prepare(self):
        self.mgr = RAIDManager.get()
        self.append(self.ui.inflate('megaraid:widget'))

    def on_start(self):
        self.mgr.refresh()
        self.find('variant').text = self.config['variant']
        arr = self.mgr.find_array(self.config['variant'])
        if arr:
            self.find('value').text = arr.state

    def create_config(self):
        return {'variant': ''}

    def on_config_start(self):
        self.mgr.refresh()
        lst = list(self.mgr.list_arrays())
        v_list = self.dialog.find('variant')
        v_list.labels = lst
        v_list.values = lst
        v_list.value = self.config['variant']

    def on_config_save(self):
        self.config['variant'] = self.dialog.find('variant').value
