"""
This module provide an interface for working with crontab.
It's using shell command 'crontab' and donn't change file manualy
"""
from ajenti.api import IConfigurable
from ajenti.com import Plugin, implements
from ajenti.utils import shell, shell_stdin


class Task():
    """Class to represent the task in crontab"""
    def __init__(self, line=''):
        if not line:
            self.m, self.h, self.dom, self.mon, self.dow = ['*'] * 5
            self.command = ''
            self.special = ''
        elif line[0] == '@':
            tlist = line.split()
            if tlist[0] == '@annually':
                self.special = '@yearly'
            elif tlist[0] == '@midnight':
                self.special = '@hourly'
            else:
                self.special = tlist[0]
            self.command = ' '.join(tlist[1:])\
                                if tlist[1] else ''
        else:
            params = line.split()
            self.m, self.h, self.dom, self.mon, self.dow = params[:5]
            self.command = ' '.join(params[5:])
            self.special = ''

    def __repr__(self):
        """task in string for write in crontab"""
        if self.special:
            string = self.special + '\t' + self.command
        else:
            string = ' '.join((self.m, self.h, self.dom, self.mon,
                          self.dow)) + '\t' + self.command
        return string


def read_crontab(user='root'):
    """Read crontab file with shell command 'crontab -l'"""
    tasks = []
    others = []
    lines = shell('crontab -l -u ' + user).split('\n')
    for line in lines:
        if not line:
            continue
        if line.startswith('no'):
            continue
        if line[0] == '#':
            others.append(line)
            continue
        try:
            tasks.append(Task(line))
        except ValueError:
            others.append(line)
            continue
    return tasks, others

def write_crontab(tasks, user='root'):
    """
    Write tasks to crontab file with shell command and stdin.
    tasks - list of instance Task class or string.
    """
    lines = '\n'.join([str(task) for task in tasks])
    lines += '\n'
    return shell_stdin('crontab - -u ' + user, lines)[1]

def fix_crontab(user='root'):
    """
    Read and comment wrong for crontab string.
    """
    cron_lines = filter(None, shell('crontab -l -u ' + user).split('\n'))
    fixed_lines = []
    for line in cron_lines:
        if shell_stdin('crontab - -u ' + user, line + '\n')[1]:
            fixed_lines.append('#' + line)
        else:
            fixed_lines.append(line)
    write_crontab(fixed_lines, user)
    return 0

def get_all_users():
    user_list = []
    for s in open('/etc/passwd', 'r').read().split('\n'):
        try:
            s = s.split(':')
            u = s[0]
            user_list.append(u)
        except:
            pass
    return sorted(user_list)
    
    
class CronConfig (Plugin):
    implements(IConfigurable)
    name = 'Cron'
    id = 'cron'
    
    def list_files(self):
        return ['/var/spool/cron/*/*']
        
