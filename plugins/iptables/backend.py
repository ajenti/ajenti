import os
import getopt

from ajenti.ui import UI
from ajenti.utils import shell


class Rule:
    states = ['NEW', 'ESTABLISHED', 'RELATED', 'INVALID']
    flags = ['SYN', 'ACK', 'FIN', 'RST', 'URG', 'PSH', 'ALL', 'NONE']

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
            prefix = ''
            while s[0].startswith('-'):
                prefix += s[0][0]
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
            if s[0] == 'tcp-flags':
                self.tcp_flags = (inv, s[1].split(','), s[2].split(','))
                continue
            if s[0] == 'state':
                self.state = (inv, s[1].split(','))
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
            self.add_option(inv, prefix, s)
        
        
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
               
    def get_ui_flags(self, desc):
        v = self.tcp_flags
        
        return UI.LayoutTableRow(
                    UI.Label(text=desc),
                    UI.Select(
                        UI.SelectOption(text='Ignore', value='ign', selected=v[1] is None),
                        UI.SelectOption(text='Are', value='nrm', selected=not v[0] and v[1] is not None),
                        UI.SelectOption(text='Are not', value='inv', selected=v[0] and v[1] is not None),
                        name='tcpflags-mode'
                    ),
                    UI.LayoutTableCell(
                        UI.LayoutTable(
                            UI.LayoutTableRow(
                                UI.Label(text='Check:'),
                                *[UI.Checkbox(text=x, name='tcpflags-vals[]', value=x, checked=x in v[2] if v[2] else False) 
                                    for x in self.flags]
                            ),
                            UI.LayoutTableRow(
                                UI.Label(text='Mask:'),
                                *[UI.Checkbox(text=x, name='tcpflags-mask[]', value=x, checked=x in v[1] if v[1] else False) 
                                    for x in self.flags]
                            )
                        ),
                        colspan=2
                    )
               )    

    def get_ui_states(self, desc):
        v = self.state
        return UI.LayoutTableRow(
                    UI.Label(text=desc),
                    UI.Select(
                        UI.SelectOption(text='Ignore', value='ign', selected=v[1] is None),
                        UI.SelectOption(text='Is', value='nrm', selected=not v[0] and v[1] is not None),
                        UI.SelectOption(text='Isn\'t', value='inv', selected=v[0] and v[1] is not None),
                        name='state-mode'
                    ),
                    UI.LayoutTableCell(
                        UI.LayoutTable(
                            UI.LayoutTableRow(
                                *[UI.Checkbox(text=x, name='state[]', value=x, checked=v[1] and x in v[1]) 
                                    for x in self.states]
                            )
                        ),
                        colspan=2
                    )
               )    
               
    def tryset(self, param, inv, args, *names):
        if args[0] in names:
            setattr(self, param, (inv, ' '.join(args[1:])))
        return args[0] in names
            
    def add_option(self, inv, prefix, s):
        self.miscopts.append(('! ' if inv else '') + prefix + ' '.join(s))
        
    def reset(self):
        self.action = 'ACCEPT'
        self.chain = 'INPUT'
        self.miscopts = []
        self.modules = []
        self.tcp_flags = (False, None, None)
        
    def __getattr__(self, attr):
        return (False, None) 
        
    def dump(self):
        return self.raw
 
    def apply_vars(self, vars):
        line = '-A ' + self.chain

        self.modules = vars.getvalue('modules', '').split()
        for m in self.modules:
            line += ' -m ' + m
            
        line += self._format_option('-p', 'protocol', vars)
        line += self._format_option('-s', 'source', vars)
        line += self._format_option('-d', 'destination', vars)
        line += self._format_option('--mac-source', 'mac_source', vars, module='mac')
        line += self._format_option('-i', 'in_interface', vars)
        line += self._format_option('-o', 'out_interface', vars)

        line += self._format_option('--sports', 'sport', vars, module='multiport')
        line += self._format_option('--dports', 'dport', vars, module='multiport')
        
        if vars.getvalue('fragmented-mode', '') == 'nrm':
            line += ' -f'
        if vars.getvalue('fragmented-mode', '') == 'inv':
            line += ' ! -f'
        
        if vars.getvalue('tcpflags-mode', '') != 'ign':
            if vars.getvalue('tcpflags-mode', '') == 'inv':
                line += ' !'
            
            mask = []
            for i in range(0, len(self.flags)):
                if vars.getvalue('tcpflags-mask[]')[i] == '1':
                    mask.append(self.flags[i])
            vals = []
            for i in range(0, len(self.flags)):
                if vars.getvalue('tcpflags-vals[]')[i] == '1':
                    vals.append(self.flags[i])

            if mask == []: 
                mask = ['NONE']
            if vals == []: 
                vals = ['NONE']

            line += ' --tcp-flags ' + ','.join(mask) + ' '  + ','.join(vals)
                       
        if vars.getvalue('state-mode', '') != 'ign':
            if not 'state' in self.modules:
                line += ' -m state'
            if vars.getvalue('state-mode', '') == 'inv':
                line += ' !'
            st = []
            for i in range(0, len(self.states)):
                if vars.getvalue('state[]')[i] == '1':
                    st.append(self.states[i])
            if st == []: 
                st = ['NONE']
            line += ' --state ' + ','.join(st)
            
        line += ' ' + ' '.join(self.miscopts)
        
        self.action = vars.getvalue('caction', 'ACCEPT')        
        if self.action == 'RUN':
            self.action = vars.getvalue('runchain', 'ACCEPT')
        
        line += ' -j ' + self.action
         
        self.__init__(line)
        
                       
    def _format_option(self, name, key, vars, flt=lambda x: x, module=None):
        if vars.getvalue(key+'-mode') == 'ign':
            return ''
        s = ''
        if module is not None:  
            if not module in self.modules:
                self.modules.append(module)
                s = ' -m '+ module
        if vars.getvalue(key+'-mode') == 'nrm':
            s += ' ' + name + ' ' + flt(vars.getvalue(key, ''))
        if vars.getvalue(key+'-mode') == 'inv':
            s += ' ! ' + name + ' ' + flt(vars.getvalue(key, ''))
        return s

                               
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
    apply_shell = 'cat /etc/iptables.up.rules | iptables-restore'
    
    def load_runtime(self):
        shell('iptables-save > /etc/iptables.up.rules')
        self.load()
    
    def apply_now(self):
        return shell(self.apply_shell)
        
    def has_autostart(self):
        return self.apply_shell in open('/etc/rc.local').read().splitlines()

    def set_autostart(self, active):
        ll = open('/etc/rc.local').read().splitlines()
        f = open('/etc/rc.local', 'w')
        saved = False
        for l in ll:
            if l == 'exit 0' and active and not saved:
                f.write(self.apply_shell + '\n')
                saved = True
            if l != self.apply_shell:
                f.write(l + '\n')
        if active and not saved:
            f.write(self.apply_shell + '\n')
        f.close()
        
    def load(self, file='/etc/iptables.up.rules'):
        self.tables = {}
        try:
            data = open(file).read().split('\n')
            while len(data)>0:
                s = data[0]
                data = data[1:]
                if s != '':
                    if s[0] == '*':
                        self.tables[s[1:]] = Table(s[1:])
                        self.tables[s[1:]].load(data)        
        except:
            self.load_runtime()
           
    def get_devices(self):
        d = []
        for l in open('/proc/net/dev').read().splitlines():
            if ':' in l:
                dev = l.split(':')[0].strip()
                d.append((dev,dev))
        return d
        
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
            
            
