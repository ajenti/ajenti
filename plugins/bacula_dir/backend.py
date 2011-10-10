from ajenti.com import *
from ajenti import apis


class Director(Plugin):
    def __init__(self):
        pass
        
    def get_status(self):
        d = apis.bacula.query('status director').split('\n')
        
        st = {'scheduled':[], 'terminated':[], 'running':[]}
        
        while len(d) > 0 and d[0] != '':
            d = d[1:]
        
        while len(d) > 1:
            if d[0].startswith('Scheduled'):
                d = d[3:]
                if len(d[0]) == 0: continue
                try:
                    sch = []
                    st['scheduled'] = sch
                    while not d[0].startswith('='):
                        c = d[0].split('  ')
                        c = [x.strip() for x in c]
                        c = filter(lambda x:x!='', c)
                        r = {
                            'level': c[0],
                            'type': c[1],
                            'priority': c[2],
                            'date': c[3],
                            'name': c[4],
                            'volume': c[5],
                        }
                        sch.append(r)
                        d = d[1:]
                except:
                    pass

            if d[0].startswith('Running'):
                d = d[1:]
                if len(d[0]) == 0: continue
                try:
                    sch = []
                    while not d[0].startswith('='):
                        d = d[1:]
                    d = d[1:]
                    st['running'] = sch
                    while not d[0].startswith('='):
                        c = d[0].split('  ')
                        c = [x.strip() for x in c]
                        c = filter(lambda x:x!='', c)
                        r = {
                            'id': c[0].split(' ')[0],
                            'level': c[0].split(' ', 1)[1],
                            'name': c[1],
                        }
                        sch.append(r)
                        d = d[1:]
                except:
                    pass        

            if d[0].startswith('Terminated'):
                d = d[1:]
                if len(d[0]) == 0: continue
                try:
                    while not d[0].startswith('='):
                        d = d[1:]
                    d = d[1:]
                    sch = []
                    st['terminated'] = sch
                    while not d[0].startswith('='):
                        if d[0].strip() == '':
                            d = d[1:]
                            continue

                    
                        c = d[0].split('  ')
                        c = [x.strip() for x in c]
                        c = filter(lambda x:x!='', c)

                        if d[0][10] == ' ':
                            c.insert(1, '')
                            
                        r = {
                            'id': c[0],
                            'level': c[1],
                            'files': c[2],
                            'bytes': c[3],
                            'status': c[4],
                            'finished': ' '.join(c[5].split(' ', 2)[:2]),
                            'name': c[5].split(' ', 2)[2],
                        }
                        sch.append(r)
                        d = d[1:]
                except:
                    raise
            d = d[1:]                    
        return st
        
    def run_job(self, name):
        print apis.bacula.query('run %s yes'%name)