from api import *
from ajenti.com import *

import MySQLdb

class MySQLDBBackend(Plugin):
    implements(IDBBackend)

    name = 'MySQL'

    conn = None
    cur = None
    
    def connect(self, host, login, password, db):
        self.conn = MySQLdb.connect(host=host, user=login, passwd=password, db=db)
        
    def disconnect(self):
        self.conn.close()

    def sql(self, query):
        res = []
        try:
            self.cur = self.conn.cursor()
            self.cur.execute(query)
            while True:
                row = self.cur.fetchone()
                if row is None:
                    break
                res.append(row)
            self.cur.close()
            return res
        except:
            return [['Invalid query']]
            
