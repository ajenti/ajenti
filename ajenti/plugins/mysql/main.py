import subprocess

from ajenti.api import *
from ajenti.plugins.configurator.api import ClassConfigEditor
from ajenti.plugins.db_common.api import DBPlugin, Database


@plugin
class MySQLClassConfigEditor (ClassConfigEditor):
    title = 'MySQL'
    icon = 'table'

    def init(self):
        self.append(self.ui.inflate('mysql:config'))


@plugin
class MySQLPlugin (DBPlugin):
    default_classconfig = {'user': 'root', 'password': ''}
    classconfig_editor = MySQLClassConfigEditor

    service_name = 'mysql'
    service_buttons = [
        {
            'command': 'reload',
            'text': 'Reload',
            'icon': 'step-forward',
        }
    ]

    def init(self):
        self.title = 'MySQL'
        self.category = 'Software'
        self.icon = 'table'

    def query(self, sql):
        p = subprocess.Popen([
            'mysql',
            '-u' + self.classconfig['user'],
            '-p' + self.classconfig['password']],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print sql
        o, e = p.communicate(sql)
        if p.returncode:
            raise Exception(e)
        return filter(None, o.splitlines()[1:])

    def query_databases(self):
        r = []
        for l in self.query('SHOW DATABASES;'):
            db = Database()
            db.name = l
            r.append(db)
        return r

    def query_drop(self, db):
        self.query("DROP DATABASE `%s`;" % db.name)
