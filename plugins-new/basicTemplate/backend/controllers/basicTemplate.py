from jadi import component
import subprocess
import os

from aj.api.http import get, post, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError
from reconfigure.configs import FSTabConfig
from reconfigure.items.fstab import FilesystemData


@component(HttpPlugin)
class Handler(HttpPlugin):

    def __init__(self, context):
        self.context = context

    @get(r'/api/basicTemplate')
    @endpoint(api=True)
    def hello_world(self, http_context):
           return "Hello World from backend"
