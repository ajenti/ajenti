from ajenti.utils import shell, shell_stdin

class Task():
    def __init__(self, line=''):
        if not line:
            self.m, self.h, self.dom, self.mon, self.dow = ['*'] * 5
            self.command = ''
        elif line[0] == '@':
            tlist = line.split()
            self.special = tlist[0]
            self.command = ' '.join(tlist[1:])\
                                if tlist[1] else ''
        else:
            params = line.split()
            self.m, self.h, self.dom, self.mon, self.dow = params[:5]
            self.command = ' '.join(params[5:])
            self.special = ''
        
    def __repr__(self):
        if self.special:
            string = self.special + '\t' + self.command
        else:
            string = ' '.join((self.m, self.h, self.dom, self.mon,
                          self.dow)) + '\t' + self.command
        return string

def read_crontab(user="root"):
    tasks = []
    others = []
    lines = shell('crontab -l').split('\n')
    for line in lines:
        if line and line[0] == '#':
            others.append(line)
            continue
        elif not line:
            continue
        try:
            tasks.append(Task(line))
        except ValueError:
            others.append(line)
            continue
    return tasks, others
    
def write_crontab(tasks, user='root'):
    lines = '\n'.join([str(task) for task in tasks])
    lines += '\n'
    return shell_stdin('crontab -', lines)[1]
    
    
