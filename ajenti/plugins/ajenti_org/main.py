import os
import gevent
import requests
import json
from datetime import datetime

from ajenti.api import *
from ajenti.api.sensors import Sensor
from ajenti.plugins import manager
from ajenti.plugins.configurator.api import ClassConfigEditor
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
import ajenti


ENDPOINT = 'http://ajenti.local.org:8080/docking-bay/receive/%i'
ENDPOINT = 'http://ajenti.org/docking-bay/receive/%i'


def _check():
    return os.path.exists('/var/lib/ajenti/.ajenti.org.enabled')


@plugin
class AjentiOrgReporterConfigEditor (ClassConfigEditor):
    title = 'ajenti.org reporter'
    icon = 'globe'

    def init(self):
        self.append(self.ui.inflate('ajenti_org:config'))


@plugin
class AjentiOrgReporter (BasePlugin):
    default_classconfig = {'key': None}
    classconfig_editor = AjentiOrgReporterConfigEditor
    classconfig_root = True

    @classmethod
    def verify(cls):
        return _check()

    def init(self):
        self.last_report = None
        self.last_error = None
        gevent.spawn(self.worker)

    @classmethod
    def classinit(cls):
        cls.get()

    def get_key(self):
        self.load_classconfig()
        if not 'key' in self.classconfig:
            return None
        return self.classconfig['key']

    def set_key(self, key):
        self.classconfig['key'] = key
        self.save_classconfig()

    def worker(self):
        if not ENDPOINT:
            return
        while True:
            datapack = {'sensors': {}}

            for sensor in Sensor.get_all():
                data = {}
                for variant in sensor.get_variants():
                    data[variant] = sensor.value(variant)
                datapack['sensors'][sensor.id] = data

            gevent.sleep(10)
            url = ENDPOINT % ajenti.config.tree.installation_id

            if not self.get_key():
                continue

            try:
                requests.post(url, data={
                    'data': json.dumps(datapack),
                    'key': self.get_key()
                })
                self.last_report = datetime.now()
                self.last_error = None
            except Exception as e:
                self.last_error = e


@plugin
class AjentiOrgSection (SectionPlugin):

    @classmethod
    def verify(cls):
        return _check()

    def init(self):
        self.title = 'Ajenti.org'
        self.icon = 'group'
        self.category = ''
        self.order = 25
        self.append(self.ui.inflate('ajenti_org:main'))
        self.reporter = AjentiOrgReporter.get(manager.context)

    def on_page_load(self):
        self.refresh()

    def refresh(self):
        key = self.reporter.get_key()
        self.find('pane-not-configured').visible = key is None
        self.find('pane-configured').visible = key is not None
        self.find('last-report').text = str(self.reporter.last_report)
        self.find('last-error').visible = self.reporter.last_error is not None
        self.find('last-error').text = str(self.reporter.last_error)

    @on('save-key', 'click')
    def on_save_key(self):
        AjentiOrgReporter.get().set_key(self.find('machine-key').value)
        self.refresh()

    @on('disconnect', 'click')
    def on_disconnect(self):
        AjentiOrgReporter.get().set_key(None)
        self.refresh()
