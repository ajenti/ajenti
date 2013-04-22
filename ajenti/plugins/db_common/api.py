from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder


class Database (object):
    def __init__(self):
        self.name = ''


class DBPlugin (SectionPlugin):
    service_name = ''
    service_buttons = []

    def init(self):
        self.append(self.ui.inflate('db_common:main'))
        self.binder = Binder(None, self)
        self.find_type('servicebar').buttons = self.service_buttons

        def delete_db(db, c):
            self.query_drop(db)
            self.refresh()

        self.find('databases').delete_item = delete_db

    def on_page_load(self):
        self.refresh()

    @on('add-db', 'click')
    def save(self):
        self.refresh()

    def refresh(self):
        try:
            self.databases = self.query_databases()
        except Exception, e:
            self.context.notify('error', str(e))

        self.binder.reset(self).autodiscover().populate()
        self.find_type('servicebar').reload()

    def query_databases(self):
        return []

    def query_drop(self, db):
        pass
