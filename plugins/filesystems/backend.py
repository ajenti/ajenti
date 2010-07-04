class Entry:
    def __new__(self):
        self.src = ''
        self.dst = ''
        self.options = ''
        self.fs_type = ''
        self.dump_p = 0
        self.fsck_p = 0
        
        
def read():
    ss = open('/etc/fstab', 'r').read().split('\n')
    r = []
    
    for s in ss:
        if s != '' and s[0] != '#':
            try:
                s = s.split()
                e = Entry()
                e.src = s[0]
                e.dst = s[1]
                e.fs_type = s[2]
                e.options = s[3]
                e.dump_p = int(s[4])
                e.fsck_p = int(s[5])
                r.append(e)
            except:
                pass

    return r
       
def save(ee):
    d = ''
    for e in ee:
        d += '%s\t%s\t%s\t%s\t%i\t%i\n' % (e.src, e.dst, e.fs_type, e.options, e.dump_p, e.fsck_p)
    with open('/etc/fstab', 'w') as f:
        f.write(d)
           
