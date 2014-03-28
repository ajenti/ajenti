import gevent
import json
import logging
import os
import requests

from ajenti.api import *
from ajenti.ipc import IPCHandler
from ajenti.plugins import manager
from ajenti.util import *


HOST = 'ajenti.org'
URL = 'http://%s/licensing-api/' % HOST
LICENSE_PATH = '/var/lib/ajenti/license'


@public
@plugin
@persistent
@rootcontext
class Licensing (BasePlugin):
    licensing_active = True

    def init(self):
        gevent.spawn(self.worker)
        self.__license_status = {}

    def get_license_status(self):
        return self.__license_status

    def read_license(self):
        if not os.path.exists(LICENSE_PATH):
            return None
        return open(LICENSE_PATH).read()

    def remove_license(self):
        if os.path.exists(LICENSE_PATH):
            os.unlink(LICENSE_PATH)
        self.__license_status = {}

    def write_license(self, key):
        open(LICENSE_PATH, 'w').write(key)
        os.chmod(LICENSE_PATH, 0600)

    def activate(self):
        response = requests.post(URL + 'activate?key=' + self.read_license())
        logging.debug('Licensing << %s' % response.content)
        response = json.loads(response.content)
        if response['status'] == 'ok' and self.__license_status == {}:
            logging.info('License activated')
        self.__license_status = response
        return self.__license_status

    def deactivate(self):
        response = requests.post(URL + 'deactivate?key=' + self.read_license())
        logging.debug('Licensing << %s' % response.content)

    def worker(self):
        while True:
            try:
                if self.read_license() is not None:
                    self.activate()
            except:
                pass
            gevent.sleep(3600 * 12)


@plugin
class LicensingIPC (IPCHandler):
    def init(self):
        self.manager = Licensing.get()

    def get_name(self):
        return 'license'

    def handle(self, args):
        command = args[0]
        if command == 'install':
            if len(args) != 2:
                return 'ajenti-ipc license install <key>'
            self.manager.write_license(args[1])
            return json.dumps(self.manager.activate())
        if command == 'remove':
            self.manager.deactivate()
            self.manager.remove_license()
            return 'OK'
