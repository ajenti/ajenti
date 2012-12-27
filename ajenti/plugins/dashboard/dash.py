from ajenti.api import *
from ajenti.api.sensors import Sensor
from ajenti.ui.binder import CollectionAutoBinding
from ajenti.ui import on, UIElement
from ajenti.plugins.main.api import SectionPlugin

from api import DashboardWidget


@plugin
class Dash (SectionPlugin):
    default_classconfig = {'widgets': []}

    def init(self):
        self.title = 'Dashboard'
        self.category = ''
        self.icon = 'dashboard'
        self.order = 0

        self.append(self.ui.inflate('dashboard:dash'))
        self.dash = self.find('dash')
        self.dash.on('reorder', self.on_reorder)

        def post_widget_bind(o, c, i, u):
            u.find('listitem').on('click', self.on_add_widget_click, i)

        self.find('add-widgets').post_item_bind = post_widget_bind
        CollectionAutoBinding(sorted(DashboardWidget.get_classes(), key=lambda x: x.name),
            None, self.find('add-widgets')).populate()

    def on_page_load(self):
        self.refresh()

    @on('refresh-button', 'click')
    def on_refresh(self):
        self.refresh()

    @on('add-button', 'click')
    def on_dialog_open(self):
        self.find('add-dialog').visible = True

    @on('add-dialog', 'button')
    def on_dialog_close(self, button):
        self.find('add-dialog').visible = False

    def on_add_widget_click(self, cls):
        self.find('add-dialog').visible = False
        self.classconfig['widgets'].append({
            'class': cls.classname,
            'container': 0,
            'index': 0,
            'config': None,
        })
        self.save_classconfig()
        self.refresh()

    def refresh(self):
        self.find('hostname').text = Sensor.find('hostname').value()

        self.dash.empty()
        for widget in self.classconfig['widgets']:
            for cls in DashboardWidget.get_classes():
                if cls.classname == widget['class']:
                    instance = cls.new(
                        self.ui,
                        container=widget['container'],
                        index=widget['index'],
                        config=widget['config']
                    )
                    instance.on('save-config', self.on_widget_config, widget, instance)
                    self.dash.append(instance)

    def on_widget_config(self, config, instance):
        config['config'] = instance.config
        self.save_classconfig()
        self.refresh()

    def on_reorder(self, indexes):
        cfg = {'widgets': []}
        for container, items in indexes.iteritems():
            idx = 0
            for item in items:
                item = self.dash.find_uid(item)
                item.container = container
                item.index = idx
                idx += 1
                cfg['widgets'].append({
                    'class': item.classname,
                    'container': item.container,
                    'index': item.index,
                    'config': item.config,
                })
        self.classconfig = cfg
        self.save_classconfig()
        self.refresh()


@plugin
class DashboardDash (UIElement):
    typeid = 'dashboard:dash'
