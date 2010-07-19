from ajenti.utils import *

def restart():
    shell('service smbd restart')
    shell('service samba restart') # older samba packages
    
class SambaConfig:
    shares = {}
    general = {}
    
    defaults = {
        'available': 'yes',
        'browseable': 'yes',
        'valid users': '',
        'path': '/dev/null',
        'read only': 'yes',
        'guest ok': 'yes',
        'guest only': 'no'
    }
    
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
        
