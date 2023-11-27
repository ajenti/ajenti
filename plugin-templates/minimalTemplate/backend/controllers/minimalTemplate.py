from jadi import component
import subprocess
import os

from aj.api.http import get, post, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError


@component(HttpPlugin)
class Handler(HttpPlugin):

    def __init__(self, context):
        self.context = context

    @get(r'/api/minimalTemplate')
    @endpoint(api=True)
    def hello_world_minimalTemplate(self, http_context):
           return "Hello World from minimalTemplate backend"
