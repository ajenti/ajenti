from jadi import component
import subprocess

from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError
from reconfigure.configs import FSTabConfig


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/get_mounted')
    @endpoint(api=True)
    def handle_api_mounted(self, http_context):

        if http_context.method == 'GET':
            filesystems = []

            mounted = subprocess.check_output(['df', '-P']).decode('utf-8')
            for entry in mounted.splitlines()[1:]:
                entry = entry.split()

                device = entry[0]
                mountpoint = entry[5] # Problem with mac os ?
                used = int(entry[2]) * 1024
                size = int(entry[1]) * 1024
                usage = used / size

                filesystems.append({
                    'device':device,
                    'mountpoint': mountpoint,
                    'used': used,
                    'size': size,
                    'usage': usage
                })

            return filesystems


    @url(r'/api/fstab')
    @endpoint(api=True)
    def handle_api_fstab(self, http_context):

        if http_context.method == 'GET':
            self.fstab_config = FSTabConfig(path='/etc/fstab-dev')
            self.fstab_config.load()
            return self.fstab_config.tree.to_dict()

