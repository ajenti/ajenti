import logging
import os
import pymongo
import subprocess
import tempfile

from ajenti.api import *
from ajenti.plugins.configurator.api import ClassConfigEditor
from ajenti.plugins.db_common.api import Database, User


@plugin
class MongoClassConfigEditor (ClassConfigEditor):
    title = 'MongoDB'
    icon = 'table'

    def init(self):
        self.append(self.ui.inflate('mongo:config'))


class MongoConnection (object):
    def __init__(self, db):
        self.client = pymongo.MongoClient(db.classconfig['url'])

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.client.disconnect()


@plugin
class MongoDB (BasePlugin):
    default_classconfig = {'url': 'mongodb://localhost:27017/'}
    classconfig_editor = MongoClassConfigEditor

    def connect(self):
        return MongoConnection(self)

    def query_sql(self, db, sql):
        f = tempfile.NamedTemporaryFile(suffix='.js', delete=False)
        f.write(sql)
        f.close()
            
        url = self.classconfig['url']
        if url.startswith('mongodb://'):
            url = url[10:]

        p = subprocess.Popen(
            [
                'mongo',
                url.rstrip('/') + '/' + db,    
                f.name,
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        o, e = p.communicate(sql)
        os.unlink(f.name)
        if p.returncode:
            raise Exception(o + e)
        return filter(None, [[x] for x in (o + e).splitlines()])

    def query_databases(self):
        r = []
        with self.connect() as mongo:
            for x in mongo.client.database_names():
                d = Database()
                d.name = x
                r.append(d)
        return r

    def query_drop(self, db):
        with self.connect() as mongo:
            return mongo.client.drop_database(db.name)

    def query_create(self, name):
        with self.connect() as mongo:
            return mongo.client[name]['_tmp'].insert(0)
