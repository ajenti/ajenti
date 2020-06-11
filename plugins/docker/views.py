from jadi import component
import subprocess
import json

from aj.api.http import url, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint, EndpointError

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context
        self.docker = ['docker']

    @url(r'/api/docker/which')
    @endpoint(api=True)
    def handle_api_which_docker(self, http_context):
        try:
            self.docker = subprocess.check_output(['which', 'docker']).decode().strip()
        except subprocess.CalledProcessError as e:
            raise EndpointError(_('Docker is not installed on this host'))

    @url(r'/api/docker/get_resources')
    @endpoint(api=True)
    def handle_api_resources_docker(self, http_context):
        command = self.docker + ['stats', '--format', '\'{{json .}}\'', '--no-stream', '-a']
        return [json.loads(line) for line in subprocess.check_output(command).decode().splitlines()]

    @url(r'/api/docker/get_details')
    @endpoint(api=True)
    def handle_api_details_container(self, http_context):
        if http_context.method == 'POST':
            container = http_context.json_body()['container']
            command = self.docker + ['inspect', container, '--format', '\'{{json .}}\'']
            return json.loads(subprocess.check_output(command).decode())

    @url(r'/api/docker/container_command')
    @endpoint(api=True)
    def handle_api_container_stop(self, http_context):
        """Possible controls are start, stop and remove, container is the hash."""
        if http_context.method == 'POST':
            container = http_context.json_body()['container']
            control = http_context.json_body()['control']
            command = self.docker + [control, container]
            try:
                subprocess.check_output(command, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                raise EndpointError(e.output.decode().strip())

    @url(r'/api/docker/list_images')
    @endpoint(api=True)
    def handle_api_list_images(self, http_context):
        command = self.docker + ['images', '--format', '\'{{json .}}\'', '--no-trunc', '-a']
        images = []
        for line in subprocess.check_output(command).decode().splitlines():
            image = json.loads(line)
            image['hash'] = image['ID'].split(':')[1][:12]
            images.append(image)
        return images

    @url(r'/api/docker/remove_image')
    @endpoint(api=True)
    def handle_api_remove_image(self, http_context):
        if http_context.method == 'POST':
            image = http_context.json_body()['image']
            command = self.docker + ['rmi', image]
            try:
                subprocess.check_output(command, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                raise EndpointError(e.output.decode().strip())

