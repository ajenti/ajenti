import subprocess


class SambaUser (object):
    def __init__(self):
        self.username = None
        self.sid = None


class SambaUsers (object):
    def load(self):
        self.users = []
        for un in [s.split(':')[0] for s in subprocess.check_output(['pdbedit', '-L', '-d0']).split('\n')]:
            if un and not ' ' in un and not un.startswith('WARNING'):
                lines = subprocess.check_output(['pdbedit', '-Lv', '-d0', '-u', un]).split('\n')
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

    def set_password(self, un, pw):
        p = subprocess.Popen(['pdbedit', '-at', '-u', un])
        p.communicate('%s\n%s\n' % (pw, pw))
        return p.returncode == 0
