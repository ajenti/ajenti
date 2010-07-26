import commands

def run(c):
    return commands.getstatusoutput(c)[0]

share_path = '/usr/share/'
etc_path = '/etc/'
bin_path = '/usr/bin/' 

def build(dir, name, ver, desc, deps, provs):
    run('mkdir ' + dir + 'DEBIAN')
    
    l = (name, ver, ', '.join(deps), ', '.join(provs), desc)
    i = 'Package: %s\nPriority: optional\nSection: admin\nArchitecture: i386\nVersion: %s\nDepends: %s\nProvides: %s\nDescription: %s\n' % l
    with open(dir + 'DEBIAN/control', 'w') as f:
        f.write(i)
        
    run('dpkg-deb -b ' + dir + ' out/' + name + '-' + ver + '.deb')
