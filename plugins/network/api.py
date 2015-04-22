from jadi import interface


@interface
class NetworkManager(object):
    def __init__(self, context):
        self.context = context

    def get_config(self):
        raise NotImplementedError

    def set_config(self, config):
        raise NotImplementedError

    def get_state(self, iface):
        raise NotImplementedError

    def up(self, iface):
        raise NotImplementedError

    def down(self, iface):
        raise NotImplementedError

    def get_hostname(self):
        raise NotImplementedError

    def set_hostname(self, value):
        raise NotImplementedError

    def restart(self):
        raise NotImplementedError
