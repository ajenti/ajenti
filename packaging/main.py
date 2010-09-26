import sys
import commands
import os

def run(c):
    return commands.getstatusoutput(c)[0]

def clean():
    run('rm -r tmp')
    run('mkdir tmp')

def ann_build(s):
    print '> Building package \'' + s  + '\''

base_desc = 'Server administration web-interface\n '

if len(sys.argv) < 3:
    print 'Usage: main.py <package format> <version number>'
    sys.exit(1)
    
pkg = __import__(sys.argv[1])
run('mkdir out') 
clean()
version = sys.argv[2]
run('cd ..;find|grep .pyc|xargs rm')    
    
ann_build('ajenti')
run('mkdir tmp/usr/share/ajenti/ajenti/ -p')
run('mkdir tmp/usr/share/ajenti/plugins/ -p')
run('mkdir tmp/usr/bin/ -p')
run('mkdir tmp/etc/ajenti -p')
if sys.argv[1] == 'arch':
    run('mkdir tmp/etc/rc.d/ -p')
else:
    run('mkdir tmp/etc/init.d/ -p')

run('cp -r ../ajenti/* tmp/usr/share/ajenti/ajenti/')
run('echo "version = \'%s\'\n" > tmp/usr/share/ajenti/ajenti/__init__.py' % version)
run('cp ../serve.py tmp/usr/share/ajenti/')
run('cp ../server.pem tmp/usr/share/ajenti/')
run('cp files/ajenti.conf tmp/etc/ajenti/')
if sys.argv[1] == 'arch':
    run('cp files/initscript tmp/etc/rc.d/ajenti')
else:
    run('cp files/initscript tmp/etc/init.d/ajenti')
run('cp files/starter tmp/usr/bin/ajenti')
run('chmod 755 tmp/usr/bin/ajenti')

deps = ['python', 'python-lxml', 'python-openssl']
pkg.build('tmp/', 'ajenti', version, base_desc, deps, [])

for p in os.listdir('../plugins'):
    try:
        ss = open('../plugins/' + p + '/info').read().split('\n')
        name = ''
        pkgname = ''
        ver = ''
        deps = []
        provs = []
        desc = ''
        only = sys.argv[1]
         
        for s in ss:
            try:
                k = s.split(' ')[0]
                v = ' '.join(s.split(' ')[1:])
                if k == 'name': name = v
                if k == 'pkg': pkgname = v
                if k == 'only': only = v
                if k == 'desc': desc = v
                if k == 'ver': ver = v
                if k == 'dep': deps.append(v)
                if k == 'prov': provs.append(v)
            except:
                pass
       
        clean()
        if only != sys.argv[1]:
            raise Exception()
            
        deps.append('ajenti')
        ann_build('ajenti-plugin-' + pkgname + '-'+ version)
        run('mkdir tmp/usr/share/ajenti/plugins/' + p + ' -p')
        run('cp -r ../plugins/' + p + '/* tmp/usr/share/ajenti/plugins/' + p)
        run('rm tmp/usr/share/ajenti/plugins/' + p + '/info')
        pkg.build('tmp/', 'ajenti-plugin-' + pkgname, version, base_desc + desc, deps, provs)
    except:
        print '  Skipping plugin ' + p

print 'Complete'
clean()
