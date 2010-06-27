import sys
import commands
import os

def run(c):
    return commands.getstatusoutput(c)[0]

def clean():
    run('rm -r tmp/*')
    run('mkdir tmp')

def ann_build(s):
    print '> Building package \'' + s  + '\''

base_desc = 'Server administration web-interface\n '

if len(sys.argv) == 1:
    print 'Usage: main.py <package format>'
    sys.exit(1)
    
pkg = __import__(sys.argv[1])
run('mkdir out')
clean()

ann_build('ajenti')
run('mkdir tmp/usr/share/ajenti/ajenti/ -p')
run('mkdir tmp/usr/lib/ajenti/plugins/ -p')
run('mkdir tmp/usr/bin/ -p')
run('mkdir tmp/etc/ajenti -p')
run('mkdir tmp/etc/init.d/ -p')

run('cp -r ../ajenti/* tmp/usr/share/ajenti/ajenti/')
run('cp ../serve.py tmp/usr/share/ajenti/')
run('cp ../server.pem tmp/usr/share/ajenti/')
run('cp files/ajenti.conf tmp/etc/ajenti/')
run('cp files/initscript tmp/etc/init.d/ajenti')
run('ln -s /usr/share/ajenti/serve.py tmp/usr/bin/ajenti')

deps = ['python2.6', 'python-genshi', 'python-openssl']
pkg.build('tmp/', 'ajenti', '0.1', base_desc, deps)

for p in os.listdir('../plugins'):
    try:
        ss = open('../plugins/' + p + '/info').read().split('\n')
        name = ''
        pkgname = ''
        ver = ''
        deps = []
        desc = ''
        
        for s in ss:
            try:
                k = s.split(' ')[0]
                v = ' '.join(s.split(' ')[1:])
                if k == 'name': name = v
                if k == 'pkg': pkgname = v
                if k == 'desc': desc = v
                if k == 'ver': ver = v
                if k == 'dep': deps.append(v)
            except:
                pass
       
        clean()
        ann_build('ajenti-plugin-' + pkgname + '-'+ ver)
        run('mkdir tmp/usr/lib/ajenti/plugins/' + p + ' -p')
        run('cp -r ../plugins/' + p + '/* tmp/usr/lib/ajenti/plugins/' + p)
        run('rm tmp/usr/lib/ajenti/plugins/' + p + '/info')
        pkg.build('tmp/', 'ajenti-plugin-' + pkgname, ver, base_desc + desc, deps)
    except:
        print 'Skipping plugin ' + p + ': no info file'

print 'Complete'
clean()
