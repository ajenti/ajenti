from ajenti.com import *
from ajenti.apis import API


class SQL(API):
    class IDBBackend(Interface):
        name = 'Unknown'

        def connect(self, host, login, password, db):
            pass

        def disconnect(self):
            pass

        def sql(self, query):
            pass
