import subprocess

from ajenti.api import *
from ajenti.plugins.db_common.api import DBPlugin, Database, User


@plugin
class PSQLPlugin (DBPlugin):
    service_name = 'postgresql'
    service_buttons = [
        {
            'command': 'reload',
            'text': _('Reload'),
            'icon': 'reload',
        }
    ]

    def init(self):
        self.title = 'PostgreSQL'
        self.category = _('Software')
        self.icon = 'table'

    def query(self, sql, db=''):
        p = subprocess.Popen([
            'su',
            'postgres',
            '-c',
            'psql -R"~~~" -A -t -c "%s" %s' % (sql, db)],
            cwd='/',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        o, e = p.communicate()
        if p.returncode:
            raise Exception(e)
        return filter(None, o.split('~~~'))

    def query_sql(self, db, sql):
        r = []
        for l in self.query(sql.replace('"', '\\"') + ';', db):
            r.append(l.split('|'))
        return r

    def query_databases(self):
        r = []
        for l in self.query('\\l'):
            db = Database()
            db.name = l.split('|')[0]
            r.append(db)
        return r

    def query_drop(self, db):
        self.query('DROP DATABASE %s;' % db.name)

    def query_create(self, name):
        self.query('CREATE DATABASE %s;' % name)

    def query_users(self):
        r = []
        for l in self.query('\\du'):
            u = User()
            u.host, u.name = '', l.split('|')[0]
            r.append(u)
        return r

    def query_create_user(self, user):
        self.query('CREATE USER %s WITH PASSWORD \'%s\';' % (user.name, user.password))

    def query_drop_user(self, user):
        self.query('DROP USER "%s";' % user.name)
