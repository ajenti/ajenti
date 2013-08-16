import subprocess


class SambaUser (object):
    def __init__(self):
        self.username = None
        self.sid = None


class SambaUsers (object):
    def load(self):
        self.users = []
        for un in [s.split(':')[0] for s in subprocess.check_output(['pdbedit', '-L']).split('\n')]:
            if un and not ' ' in un:
                lines = subprocess.check_output(['pdbedit', '-Lv',  '-u', un]).split('\n')
                fields = {}
                for l in lines:
                    if l and ':' in l:
                        l = l.split(':', 1)
                        fields[l[0]] = l[1].strip()
                u = SambaUser()
                u.username = un
                u.sid = fields['User SID']
                self.users.append(u)

    def create(self, un):
        p = subprocess.Popen(['pdbedit', '-at', '-u', un])
        p.communicate('\n\n\n')

    def delete(self, un):
        subprocess.call(['pdbedit', '-x', '-u', un])

    def set_password(self, un, p):
        p = subprocess.Popen(['smbpasswd', '-s', un])
        p.communicate('%s\n%s\n' % (p, p))
        return p.returncode == 0
