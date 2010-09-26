import commands

def run(c):
    return commands.getstatusoutput(c)[0]

share_path = '/usr/share/'
etc_path = '/etc/'
bin_path = '/usr/bin/' 

def build(dir, name, ver, desc, deps, provs):
    run('mkdir ' + dir + 'DEBIAN')
    if name == 'ajenti':
        run('echo "#!/bin/sh\nupdate-rc.d ajenti start 2 3 4 5 . stop 0 1 6 .; exit 0" > %sDEBIAN/postinst'%dir)
        run('echo "#!/bin/sh\nupdate-rc.d -f ajenti remove; exit 0" > %sDEBIAN/postrm'%dir)
        run('chmod 755 %sDEBIAN/post*'%dir)
        run('echo /etc/ajenti/ajenti.conf > %sDEBIAN/conffiles'%dir)
    
    l = (name, ver, ', '.join(deps))
    i = 'Package: %s\nPriority: optional\nSection: admin\nArchitecture: all\nVersion: %s\nDepends: %s\n' % l
    if provs != []:
        i += 'Provides: %s\n' % ', '.join(provs)
    i += 'Description: %s\n' % desc
    with open(dir + 'DEBIAN/control', 'w') as f:
        f.write(i)
        
    run('dpkg-deb -b ' + dir + ' out/' + name + '-' + ver + '.deb')
