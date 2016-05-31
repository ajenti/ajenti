import time
from jadi import interface


@interface
class TZManager(object):
    def __init__(self, context):
        self.context = context

    def get_tz(self):
        raise NotImplementedError

    def set_tz(self, name):
        raise NotImplementedError

    def list_tz(self):
        raise NotImplementedError

    def get_offset(self):
        return -(time.altzone if (time.daylight and time.localtime().tm_isdst > 0) else time.timezone)
