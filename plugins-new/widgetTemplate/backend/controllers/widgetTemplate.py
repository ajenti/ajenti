import psutil
from jadi import component
from aj.api.http import get, HttpPlugin
from aj.api.endpoint import endpoint
import logging

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @get(r'/api/widgetTemplate/widgetTemplate')
    @endpoint(api=True)
    def hello_widget(self, http_context):
        return "Hello Widget"
