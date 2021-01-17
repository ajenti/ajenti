"""
Module to handle the fstab file with the help of the reconfigure module.
"""

from jadi import component
import subprocess
import os

from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError
from reconfigure.configs import FSTabConfig
from reconfigure.items.fstab import FilesystemData


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/get_mounted')
    @endpoint(api=True)
    def handle_api_mounted(self, http_context):
        """
        Parse the output of the df command to generate a dict of mount devices.
        Method GET.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Details of mounted devices
        :rtype: dict
        """

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

    @url(r'/api/umount')
    @endpoint(api=True)
    def handle_api_umount(self, http_context):
        """
        Umount some device.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Success or not
        :rtype: bool or throw error
        """

        if http_context.method == 'POST':
            mountpoint = http_context.json_body()['mountpoint']
            try:
                subprocess.check_output(['umount', mountpoint])
                return True
            except Exception as e:
                raise EndpointError(e)

    @url(r'/api/fstab')
    @endpoint(api=True)
    def handle_api_fstab(self, http_context):
        """
        Load (through get) and write (through post) the fstab file.
        Make a backup when save a new fstab file.
        Method GET.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Fstab as dict in load mode, success or not in save mode
        :rtype: dict in load mode, bool or throw error in save mode
        """

        if http_context.method == 'GET':
            self.fstab_config = FSTabConfig(path='/etc/fstab')
            self.fstab_config.load()
            return self.fstab_config.tree.to_dict()

        if http_context.method == 'POST':
            config = http_context.json_body()['config']
            new_fstab = FSTabConfig(content='')
            new_fstab.load()

            for filesystem in config:
                device = FilesystemData()
                for prop, value in filesystem.items():
                    setattr(device, prop, value)
                new_fstab.tree.filesystems.append(device)

            data = new_fstab.save()[None]

            # Always make a backup
            os.rename('/etc/fstab', '/etc/fstab.bak')

            try:
                with open('/etc/fstab', 'w') as f:
                    f.write(data)
                return True
            except Exception as e:
                raise EndpointError(e)



