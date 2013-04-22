from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder


class Database (object):
    def __init__(self):
        self.name = ''


class User (object):
    def __init__(self):
        self.name = ''
        self.host = ''


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

        def delete_user(user, c):
            self.query_drop_user(user)
            self.refresh()

        self.find('users').delete_item = delete_user

    def on_page_load(self):
        self.refresh()

    @on('add-db', 'click')
    def on_add_db(self):
        self.find('db-name-dialog').value = ''
        self.find('db-name-dialog').visible = True

    @on('add-user', 'click')
    def on_add_user(self):
        self.find('add-user-dialog').visible = True

    def refresh(self):
        try:
            self.databases = self.query_databases()
            self.users = self.query_users()
        except Exception, e:
            self.context.notify('error', str(e))

        self.binder.reset(self).autodiscover().populate()
        self.find_type('servicebar').reload()

    @on('db-name-dialog', 'button')
    def on_db_name_dialog_close(self, button=None):
        self.find('db-name-dialog').visible = False

    @on('db-name-dialog', 'submit')
    def on_db_name_dialog_submit(self, value=None):
        self.query_create(value)
        self.refresh()

    @on('add-user-dialog', 'button')
    def on_add_user_dialog(self, button=None):
        d = self.find('add-user-dialog')
        d.visible = False
        u = User()
        u.name = d.find('name').value
        u.host = d.find('host').value
        u.password = d.find('password').value
        self.query_create_user(u)
        self.refresh()

    def query_databases(self):
        return []

    def query_drop(self, db):
        pass

    def query_create(self, name):
        pass

    def query_users(self):
        return []

    def query_create_user(self, user):
        pass

    def query_drop_user(self, user):
        pass
