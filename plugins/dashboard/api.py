from aj.api import *


@interface
class Widget (object):
    id = None
    name = None
    template = None
    config_template = None

    def __init__(self, context):
        self.context = context
