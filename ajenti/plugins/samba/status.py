import os
import subprocess


class SambaMonitor (object):
    def __init__(self):
        self.refresh()

    def refresh(self):
        pids = {}

        ll = subprocess.check_output(['smbstatus', '-p']).splitlines()
        for l in ll[4:]:
            s = l.split()
            if len(s) > 0:
                pids[s[0]] = (s[1], ' '.join(s[3:]))

        self.connections = []
        ll = subprocess.check_output(['smbstatus', '-S']).splitlines()
        for l in ll[3:]:
            s = l.split()
            if len(s) > 0 and s[1] in pids:
                c = SambaConnection(s[0], s[1], *pids[s[1]])
                self.connections.append(c)


class SambaConnection (object):
    def __init__(self, share, pid, user, machine):
        self.share, self.pid, self.user, self.machine = share, pid, user, machine

    def disconnect(self):
        os.kill(int(self.pid), 15)
