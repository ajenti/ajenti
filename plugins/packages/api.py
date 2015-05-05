from jadi import interface


class Package(object):
    def __init__(self, manager):
        self.manager = manager
        self.id = None
        self.name = None
        self.version = None
        self.description = None
        self.is_installed = None
        self.is_upgradeable = None
        self.installed_version = None


@interface
class PackageManager(object):
    id = None
    name = None
    update_command = None

    def __init__(self, context):
        self.context = context

    def list(self, query=None):
        raise NotImplementedError

    def get_package(self, _id):
        raise NotImplementedError

    def update_lists(self, progress_callback):
        raise NotImplementedError

    def get_apply_cmd(self, selection):
        raise NotImplementedError
