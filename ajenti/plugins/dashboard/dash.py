import random
import traceback

import ajenti
from ajenti.api import *
from ajenti.api.sensors import Sensor
from ajenti.ui.binder import CollectionAutoBinding
from ajenti.ui import on, UIElement, p
from ajenti.plugins.main.api import SectionPlugin, intent

from api import DashboardWidget


@plugin
class Dash (SectionPlugin):
    default_classconfig = {'widgets': []}

    def init(self):
        self.title = _('Dashboard')
        self.category = ''
        self.icon = 'dashboard'
        self.order = 0

        self.append(self.ui.inflate('dashboard:dash'))
        self.dash = self.find('dash')
        self.dash.on('reorder', self.on_reorder)

        self.find('header').platform = ajenti.platform_unmapped
        self.find('header').distro = ajenti.platform_string

        def post_widget_bind(o, c, i, u):
            u.find('listitem').on('click', self.on_add_widget_click, i)

        self.find('add-widgets').post_item_bind = post_widget_bind

        classes = [x for x in DashboardWidget.get_classes() if not x.hidden]
        CollectionAutoBinding(
            sorted(classes, key=lambda x: x.name),
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

    def on_add_widget_click(self, cls, config=None):
        self.add_widget(cls, config)

    def add_widget(self, cls, config=None):
        self.find('add-dialog').visible = False
        self.classconfig['widgets'].append({
            'class': cls.classname,
            'container': random.randrange(0, 2),
            'index': 0,
            'config': config,
        })
        self.save_classconfig()
        self.refresh()

    @intent('dashboard-add-widget')
    def add_widget_intent(self, cls=None, config=None):
        self.add_widget(cls, config)
        self.activate()

    def refresh(self):
        self.find('header').hostname = Sensor.find('hostname').value()

        self.dash.empty()
        for widget in self.classconfig['widgets']:
            for cls in DashboardWidget.get_classes():
                if cls.classname == widget['class']:
                    try:
                        instance = cls.new(
                            self.ui,
                            container=widget['container'],
                            index=widget['index'],
                            config=widget['config'],
                        )
                    except Exception, e:
                        traceback.print_exc()
                        instance = CrashedWidget.new(
                            self.ui,
                            container=widget['container'],
                            index=widget['index'],
                            config=widget['config'],
                        )
                        instance.classname = cls.classname
                        instance.set(e)
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


@p('platform')
@p('hostname')
@p('distro')
@plugin
class DashboardHeader (UIElement):
    typeid = 'dashboard:header'


@plugin
class CrashedWidget (DashboardWidget):
    hidden = True
    
    def init(self):
        self.append(self.ui.create('label', id='text'))

    def set(self, e):
        self.find('text').text = 'Widget crashed: ' + str(e)
