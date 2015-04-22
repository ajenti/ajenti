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
