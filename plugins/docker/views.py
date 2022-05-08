"""
Simple module to get informations from docker host on 10.0.0.3
"""

from jadi import component
import subprocess
import json

from aj.api.http import get, post, delete, HttpPlugin
# from aj.auth import authorize
from aj.api.endpoint import endpoint, EndpointError

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context
        self.docker = 'docker'

    @get(r'/api/docker/which')
    @endpoint(api=True)
    def handle_api_which_docker(self, http_context):
        """
        Test if docker is installed and retrieve docker version.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        try:
            self.docker = [subprocess.check_output(['which', 'docker']).decode().strip()]
        except subprocess.CalledProcessError as e:
            raise EndpointError(_('Docker is not installed on this host'))

    @get(r'/api/docker/containers')
    @endpoint(api=True)
    def handle_api_resources_docker(self, http_context):
        """
        Retrieve stats informations (memory, cpu, ... ) from docker and load one
        json per container in a list.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Json informations per container
        :rtype: list of json
        """

        command = self.docker + ['stats', '--format', '{{json .}}', '--no-stream', '-a']
        return [
            json.loads(line)
            for line in subprocess.check_output(command).decode().splitlines()
        ]

    @get(r'/api/docker/container/(?P<container_id>.*)')
    @endpoint(api=True)
    def handle_api_details_container(self, http_context, container_id=None):
        """
        Retrieve all informations from docker inspect for one container.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param container_id: Id of the container
        :type container_id: basestring
        :return: All container informations
        :rtype: json
        """

        command = self.docker + ['inspect', container_id, '--format', '{{json .}}']
        return json.loads(subprocess.check_output(command).decode())

    @post(r'/api/docker/container_command')
    @endpoint(api=True)
    def handle_api_container_stop(self, http_context):
        """
        Some controls for container : start, stop and remove.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        container_id = http_context.json_body()['container_id']
        control = http_context.json_body()['control']

        if control in ['start', 'stop', 'rm']:
            command = self.docker + [control, container_id]
        else:
            return http_context.respond_not_found()

        try:
            subprocess.check_output(command, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            raise EndpointError(e.output.decode().strip())

    @get(r'/api/docker/images')
    @endpoint(api=True)
    def handle_api_list_images(self, http_context):
        """
        List all images contained on the docker host.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All informations from all images
        :rtype: list of json
        """

        command = self.docker + ['images', '--format', '{{json .}}', '--no-trunc', '-a']
        images = []
        for line in subprocess.check_output(command).decode().splitlines():
            image = json.loads(line)
            image['hash'] = image['ID'].split(':')[1][:12]
            images.append(image)
        return images

    @delete(r'/api/docker/image/(?P<image_id>.*)')
    @endpoint(api=True)
    def handle_api_remove_image(self, http_context, image_id=None):
        """
        Delete one image (given as hash) on the docker host.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        command = self.docker + ['rmi', image_id]
        try:
            subprocess.check_output(command, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            raise EndpointError(e.output.decode().strip())

