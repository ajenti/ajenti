import os

from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui.binder import Binder


class AvailabilitySymlinks (object):
    """
    Manage directories of following style:
    --sites.available
     |-a.site
     --b.site
    --sites.enabled
     --a.site -> ../sites.available/a.site
    """

    def __init__(self, dir_a, dir_e):
        self.dir_a, self.dir_e = dir_a, dir_e

    def list_available(self):
        return os.listdir(self.dir_a)

    def is_enabled(self, entry):
        return self.find_link(entry) is not None

    def find_link(self, entry):
        path = os.path.join(self.dir_a, entry)
        path = os.path.abspath(path)

        for e in os.listdir(self.dir_e):
            if os.path.abspath(os.path.realpath(os.path.join(self.dir_e, e))) == path:
                return e

    def enable(self, entry):
        e = self.find_link(entry)
        if not e:
            os.symlink(os.path.join(self.dir_a, entry), os.path.join(self.dir_e, entry))

    def disable(self, entry):
        e = self.find_link(entry)
        if e:
            os.unlink(os.path.join(self.dir_e, e))

    def delete(self, entry):
        self.disable(entry)
        os.unlink(self.dir_a, entry)

    def open(self, entry, mode='r'):
        return open(os.path.join(self.dir_a, entry), mode)

    def exists(self):
        return os.path.exists(self.dir_a) and os.path.exists(self.dir_e)


class WebserverHost (object):
    def __init__(self, dir, entry):
        self.name = entry
        self.dir = dir
        self.active = dir.is_enabled(entry)
        self.config = dir.open(entry).read()

    def save(self):
        self.dir.open(self.name, 'w').write(self.config)
        if self.active:
            self.dir.enable(self.name)
        else:
            self.dir.disable(self.name)


class WebserverPlugin (SectionPlugin):
    service_name = ''
    service_buttons = []
    hosts_available_dir = ''
    hosts_enabled_dir = ''

    def init(self):
        self.append(self.ui.inflate('webserver_common:main'))
        self.binder = Binder(None, self)
        self.find_type('servicebar').buttons = self.service_buttons
        self.hosts_dir = AvailabilitySymlinks(self.hosts_available_dir, self.hosts_enabled_dir)

    def on_page_load(self):
        self.refresh()

    def refresh(self):
        self.hosts = [WebserverHost(self.hosts_dir, x) for x in self.hosts_dir.list_available()]
        self.binder.reset(self).autodiscover().populate()
        self.find_type('servicebar').reload()
