class Rule:

    def __init__(self, line):
        self.raw = line
        d = line.split()
        self.chain = d[1]
        self.action = d[-1]
        
    def dump(self):
        return self.raw
        
class Chain:
    rules = None
    
    def __init__(self, name, default):
        self.rules = []
        self.name = name
        self.comment = None
        self.default = default
        
    def dump(self):
        s = ''
        for r in self.rules:
            s += '%s\n' % r.dump()
        return s
        
class Table:
    chains = None
    
    def __init__(self, name):
        self.chains = {}
        self.name = name
    
    def load(self, data):
        while len(data)>0:
            s = data[0]
            if s.startswith('*'):
                return
            elif s.startswith(':'):
                n,d = s.split()[0:2]
                n = n[1:]
                self.chains[n] = Chain(n, d)
            elif s.startswith('-'):
                r = Rule(s)
                self.chains[r.chain].rules.append(r)
            data = data[1:]
                
    def dump(self):
        s = '*%s\n' % self.name
        for r in self.chains:
            r = self.chains[r]
            s += ':%s %s [0:0]\n' % (r.name, r.default)
        for r in self.chains:
            r = self.chains[r]
            s += '%s' % r.dump()
        s += 'COMMIT\n'
        return s        
        
        
class Config:
    tables = {}
    
    def load(self, file):
        data = open(file).read().split('\n')
        self.tables = {}
        while len(data)>0:
            s = data[0]
            data = data[1:]
            if s != '':
                if s[0] == '*':
                    self.tables[s[1:]] = Table(s[1:])
                    self.tables[s[1:]].load(data)        
                    
    def dump(self):
        s = ''
        for r in self.tables:
            s += '%s\n' % self.tables[r].dump()
        return s    
        
    def save(self, file):
        open(file, 'w').write(self.dump())
            
            
