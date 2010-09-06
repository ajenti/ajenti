import commands

def run(c):
    return commands.getstatusoutput(c)[0]

trans = {
    'python-openssl': 'pyopenssl',
    'python-mysqldb': 'mysql-python',
    'python2.6': 'python'
} 

def build(dir, name, ver, desc, deps, provs):
    dps = []
    for x in deps:
        if x in trans.keys():
            dps.append(trans[x])
        else:
            dps.append(x)
    
    name = name.replace('-','_')
    ver += '-0'
    l = (name, ver, desc, ''.join(['depend = '+x+'\n' for x in dps]), ''.join(['provides = '+x+'\n' for x in provs]))
    i = 'pkgname = %s\npkgver = %s\npkgdesc = %s\narch = any\n%s%s' % l
    with open(dir + '.PKGINFO', 'w') as f:
        f.write(i)
        f.close()
        
    run('cd '+dir+';tar -Jcf ../out/' + name + '-' + ver + '.tar.xz * .PKGINFO')
