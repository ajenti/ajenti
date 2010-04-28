from ajenti.com import *
from ajenti.app.api import *

class IDBBackend(Interface):
    name = 'Unknown'

    def connect(self, host, login, password, db):
        pass

    def disconnect(self):
        pass

    def sql(self, query):
        pass
        
