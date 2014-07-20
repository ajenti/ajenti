from ajenti.api import *
from ajenti.plugins.db_common.api import DBPlugin
from ajenti.util import platform_select

from api import MongoDB


@plugin
class MongoDBPlugin (DBPlugin):
    config_class = MongoDB
    has_users = False

    service_name = platform_select(
        default='mongod'
    )

    def init(self):
        self.title = 'MongoDB'
        self.category = _('Software')
        self.icon = 'table'
        self.db = MongoDB.get()

    def query_sql(self, db, sql):
        return self.db.query_sql(db, sql)

    def query_databases(self):
        return self.db.query_databases()

    def query_drop(self, db):
        return self.db.query_drop(db)

    def query_create(self, name):
        return self.db.query_create(name)
