import logging
import os
import rethinkdb as r
import subprocess
import tempfile

from ajenti.api import *
from ajenti.plugins.configurator.api import ClassConfigEditor
from ajenti.plugins.db_common.api import Database, User


@plugin
class RethinkClassConfigEditor (ClassConfigEditor):
    title = 'RethinkDB'
    icon = 'table'

    def init(self):
        self.append(self.ui.inflate('rethink:config'))


class RethinkConnection (object):
    def __init__(self, db):
        self.client = r.connect(host=db.classconfig['RETHINKDB_HOST'],
                         port=db.classconfig['RETHINKDB_PORT'],
                         auth_key=str(db.classconfig['RETHINKDB_AUTH']))

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.client.close()


@plugin
class RethinkDB (BasePlugin):
    default_classconfig = { 
                            'RETHINKDB_HOST': 'localhost',
                            'RETHINKDB_PORT': '28015',
                            'RETHINKDB_AUTH': ''
                        }
    classconfig_editor = RethinkClassConfigEditor

    def connect(self):
        return RethinkConnection(self)

    def query_sql(self, db, sql):
        with self.connect() as rethink:
            #FIXME: Need security for sql
            result =  eval('r.db(\'%s\').%s.run(rethink.client)'%(db,sql))
            return [[x] for x in str(result).splitlines()]

    def query_databases(self):
        result = []
        with self.connect() as rethink:
            for x in r.db_list().run(rethink.client):
                d = Database()
                d.name = x
                result.append(d)
        return result

    def query_drop(self, db):
        with self.connect() as rethink:
            return r.db_drop(db).run(rethink.client)

    def query_create(self, name):
        with self.connect() as rethink:
            return r.db_create(name).run(rethink.client)
