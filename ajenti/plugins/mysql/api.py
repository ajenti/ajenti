import logging
import subprocess

from ajenti.api import *
from ajenti.plugins.configurator.api import ClassConfigEditor
from ajenti.plugins.db_common.api import Database, User


@plugin
class MySQLClassConfigEditor (ClassConfigEditor):
    title = 'MySQL'
    icon = 'table'

    def init(self):
        self.append(self.ui.inflate('mysql:config'))


@plugin
class MySQLDB (BasePlugin):
    default_classconfig = {'user': 'root', 'password': '', 'hostname': 'localhost'}
    classconfig_editor = MySQLClassConfigEditor

    def query(self, sql, db=''):
        self.host = self.classconfig.get('hostname', None)
        self.username = self.classconfig['user']
        self.password = self.classconfig['password']
        p = subprocess.Popen(
            [
                'mysql',
                '-u' + self.username,
            ] + 
            ([
                '-p' + self.password,
            ] if self.password else []) + 
            [
                '-h', self.host or 'localhost',
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        sql = (('USE %s; ' % db) if db else '') + sql
        logging.debug(sql)
        o, e = p.communicate(sql)
        if p.returncode:
            raise Exception(e)
        return filter(None, o.splitlines()[1:])

    def query_sql(self, db, sql):
        r = []
        for l in self.query(sql + ';', db):
            r.append(l.split('\t'))
        return r

    def query_databases(self):
        r = []
        for l in self.query('SHOW DATABASES;'):
            db = Database()
            db.name = l
            r.append(db)
        return r

    def query_drop(self, db):
        self.query("DROP DATABASE `%s`;" % db.name)

    def query_create(self, name):
        self.query("CREATE DATABASE `%s` CHARACTER SET UTF8;" % name)

    def query_users(self):
        r = []
        for l in self.query('USE mysql; SELECT * FROM user;'):
            u = User()
            u.host, u.name = l.split('\t')[:2]
            r.append(u)
        return r

    def query_create_user(self, user):
        self.query("CREATE USER `%s`@`%s` IDENTIFIED BY '%s'" % (user.name, user.host, user.password))

    def query_drop_user(self, user):
        self.query("DROP USER `%s`@`%s`" % (user.name, user.host))

    def query_grant(self, user, db):
        self.query("GRANT ALL PRIVILEGES ON `%s`.* TO `%s`@`%s`" % (db.name, user.name, user.host))
        self.query("FLUSH PRIVILEGES")
