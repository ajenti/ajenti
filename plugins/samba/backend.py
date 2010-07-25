from ajenti.utils import *
import os

def restart():
    shell('service smbd restart')
    shell('service samba restart') # older samba packages
    
class SambaConfig:
    shares = {}
    general = {}
    users = {}
    
    defaults = {
        'available': 'yes',
        'browseable': 'yes',
        'valid users': '',
        'path': '/dev/null',
        'read only': 'yes',
        'guest ok': 'yes',
        'guest only': 'no'
    }
    
    editable = {
        'Account Flags': '-c',
        'User SID': '-U',
        'Primary Group SID': '-G',
        'Full Name': '-f',
        'Home Directory': '-h',
        'HomeDir Drive': '-D',
        'Logon Script': '-S',
        'Profile Path': '-p',
        'Kickoff time': '-K'
    }
    
    fields = []
    
    def load(self):
        self.shares = {}
        ss = open('/etc/samba/smb.conf', 'r').read().split('\n')
        cs = ''
        for s in ss:
            s = s.strip()
            try:
                if s[0] != '#' and s[0] != ';':
                    if s[0] == '[':
                        cs = s[1:-1]
                        self.shares[cs] = self.new_share() if cs != 'global' else {}
                    else:
                        s = s.split('=')
                        self.shares[cs][s[0].strip()] = s[1].strip()
            except:
                pass

        self.general = self.shares['global']
        self.shares.pop('global')

        self.users = {}
        ss = [s.split(',')[0].split(':')[0] for s in shell('pdbedit -L').split('\n')]
        for s in ss:
            x = shell('pdbedit -L -v -u ' + s).split('\n')
            self.users[s] = {}
            self.fields = []
            for l in x:
                try:
                    self.fields.append(l.split(':')[0])
                    self.users[s][l.split(':')[0]] = l.split(':')[1].strip()
                except:
                    pass
            
                        
    def save(self):
        with open('/etc/samba/smb.conf', 'w') as f:
            f.write('[global]\n')
            for k in self.general:
                f.write('%s = %s\n' % (k,self.general[k]))
            for s in self.shares:
                f.write('\n[%s]\n' % s)
                for k in self.shares[s]:    
                    if not k in self.defaults or self.shares[s][k] != self.defaults[k]:
                        f.write('%s = %s\n' % (k,self.shares[s][k]))
    
    def modify_user(self, u, p, v):
        shell('pdbedit -r -u %s %s "%s"' % (u,self.editable[p],v))
                 
    def del_user(self, u):
        shell('pdbedit -x -u ' + u)
                        
    def add_user(self, u):
        with open('/tmp/pdbeditnn', 'w') as f:
            f.write('\n\n\n')
        shell('pdbedit -a -t -u ' + u + ' < /tmp/pdbeditnn')
        os.unlink('/tmp/pdbeditnn')
                                        
    def get_shares(self):
        return self.shares.keys()                                          
        
    def new_share(self):
        return self.defaults.copy()
        
    def set_param(self, share, param, value):
        self.shares[share][param] = value
                
    def set_param_from_vars(self, share, param, vars):
        value = vars.getvalue(param, self.defaults[param])
        self.set_param(share, param, value)
        
    def set_param_from_vars_yn(self, share, param, vars):
        value = 'yes' if vars.getvalue(param, self.defaults[param]) == '1' else 'no'
        self.set_param(share, param, value)
        
