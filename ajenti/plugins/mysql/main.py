from ajenti.api import *
from ajenti.plugins.db_common.api import DBPlugin

from api import MySQLDB


@plugin
class MySQLPlugin (DBPlugin):
    config_class = MySQLDB

    service_name = 'mysql'
    service_buttons = [
        {
            'command': 'reload',
            'text': _('Reload'),
            'icon': 'step-forward',
        }
    ]

    def init(self):
        self.title = 'MySQL'
        self.category = _('Software')
        self.icon = 'table'
        self.db = MySQLDB.get()

    def query_sql(self, db, sql):
        return self.db.query_sql(db, sql)

    def query_databases(self):
        return self.db.query_databases()

    def query_drop(self, db):
        return self.db.query_drop(db)

    def query_create(self, name):
        return self.db.query_create(name)

    def query_users(self):
        return self.db.query_users()

    def query_create_user(self, user):
        return self.db.query_create_user(user)

    def query_drop_user(self, user):
        return self.db.query_drop_user(user)

    def query_grant(self, user, db):
        return self.db.query_grant(user, db)
