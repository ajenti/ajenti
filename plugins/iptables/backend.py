import os
import getopt

from ajenti.ui import UI
from ajenti.utils import shell


class Rule:

    def __init__(self, line='-A INPUT -j ACCEPT'):
        self.reset()
        self.raw = line
        opts = line.split()
        self.desc = ' '.join(opts[2:-2])
     
        while len(opts) > 0:
            inv = False
            if opts[0] == '!':
                inv = True
                opts = opts[1:]
            s = [opts[0]]
            while s[0].startswith('-'):
                s[0] = s[0][1:]
            opts = opts[1:]
            while len(opts) > 0 and not opts[0].startswith('-'):
                if opts[0] == '!':
                    break
                else:
                    s.append(opts[0])
                    opts = opts[1:]

            # S is one option
            if s[0] == 'f':
                self.fragment = (inv, True)
                continue
            if s[0] == 'A':
                self.chain = s[1]
                continue
            if s[0] == 'j':
                self.action = s[1]
                continue
            if s[0] == 'm':
                self.modules.append(s[1])
                continue

            self.tryset('protocol', inv, s, 'p', 'protocol') or \
            self.tryset('source', inv, s, 's', 'src') or \
            self.tryset('destination', inv, s, 'd', 'dst') or \
            self.tryset('mac_source', inv, s, 'mac-source') or \
            self.tryset('in_interface', inv, s, 'i', 'in-interface') or \
            self.tryset('out_interface', inv, s, 'i', 'in-interface') or \
            self.tryset('sport', inv, s, 'sport', 'source-port') or \
            self.tryset('dport', inv, s, 'dport', 'destination-port') or \
            self.tryset('sport', inv, s, 'sports', 'source-ports') or \
            self.tryset('dport', inv, s, 'dports', 'destination-ports') or \
            self.add_option(inv, s)
        
        
    def get_ui_text(self, param, desc):
        v = getattr(self, param)
        return UI.LayoutTableRow(
                    UI.Label(text=desc),
                    UI.Select(
                        UI.SelectOption(text='Ignore', value='ign', selected=v[1] is None),
                        UI.SelectOption(text='Is', value='nrm', selected=not v[0] and v[1] is not None),
                        UI.SelectOption(text='Isn\'t', value='inv', selected=v[0] and v[1] is not None),
                        name='%s-mode'%param
                    ),
                    UI.TextInput(name=param, value=v[1] or '')
               )

    def get_ui_bool(self, param, desc):
        v = getattr(self, param)
        return UI.LayoutTableRow(
                    UI.Label(text=desc),
                    UI.Select(
                        UI.SelectOption(text='Ignore', value='ign', selected=v[1] is None),
                        UI.SelectOption(text='Yes', value='nrm', selected=v[1]==True),
                        UI.SelectOption(text='No', value='inv', selected=v[1]==False),
                        name='%s-mode'%param
                    )
               )

    def get_ui_select(self, param, desc, opts, size=10):
        # opts == [['Desc', 'value'], ['Desc #2', 'value2']]
        v = getattr(self, param)
        
        return UI.LayoutTableRow(
                    UI.Label(text=desc),
                    UI.Select(
                        UI.SelectOption(text='Ignore', value='ign', selected=v[1] is None),
                        UI.SelectOption(text='Is', value='nrm', selected=not v[0] and v[1] is not None),
                        UI.SelectOption(text='Isn\'t', value='inv', selected=v[0] and v[1] is not None),
                        name='%s-mode'%param
                    ),
                    UI.SelectTextInput(
                        *[UI.SelectOption(text=x[0], value=x[1], selected=v[1]==x[1])
                            for x in opts],
                        name=param,
                        value=v[1] or '',
                        size=size
                    )
               )
    
    def tryset(self, param, inv, args, *names):
        if args[0] in names:
            setattr(self, param, (inv, ' '.join(args[1:])))
        return args[0] in names
            
    def add_option(self, inv, s):
        self.miscopts.append(('! ' if inv else '') + ' '.join(s))
        
    def reset(self):
        self.action = 'ACCEPT'
        self.chain = 'INPUT'
        self.miscopts = []
        self.modules = []
        
    def __getattr__(self, attr):
        return (False, None) 
        
    def dump(self):
        return self.raw
        
    def summary(self):
        return ''
        
        
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
    
    def load_runtime(self):
        shell('iptables-save > /tmp/ajenti-iptables')
        load('/tmp/ajenti-iptables')
        os.unlink('/tmp/ajenti-iptables')
    
    def load(self, file='/etc/iptables.up.rules'):
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
        
    def save(self, file='/etc/iptables.up.rules'):
        open(file, 'w').write(self.dump())
            
    def table_index(self, name):
        i = 0
        for t in self.tables:
            if self.tables[t].name == name:
                return i
            i += 1
            
            
