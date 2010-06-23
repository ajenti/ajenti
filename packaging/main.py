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
run('mkdir tmp' + pkg.share_path + 'ajenti/ajenti/ -p')
run('mkdir tmp' + pkg.share_path + 'ajenti/plugins/ -p')
run('mkdir tmp' + pkg.bin_path + ' -p')
run('mkdir tmp' + pkg.etc_path + 'ajenti -p')

run('cp -r ../ajenti/* tmp' + pkg.share_path + 'ajenti/ajenti/')
run('cp ../plugins/__init__.py tmp' + pkg.share_path + 'ajenti/plugins/')
run('cp ../serve.py tmp' + pkg.share_path + 'ajenti/')
run('cp ../server.pem tmp' + pkg.share_path + 'ajenti/')
run('cp ../ajenti.conf tmp' + pkg.etc_path + 'ajenti/')
run('echo \'#!/bin/bash\' > tmp/' + pkg.bin_path + 'ajenti')
run('echo cd ' + pkg.share_path + 'ajenti/ >> tmp/' + pkg.bin_path + 'ajenti')
run('echo python ' + pkg.share_path + 'ajenti/serve.py >> tmp/' + pkg.bin_path + 'ajenti')
run('chmod +x tmp/' + pkg.bin_path + 'ajenti')

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
        run('mkdir tmp' + pkg.share_path + 'ajenti/plugins/' + p + ' -p')
        run('cp -r ../plugins/' + p + '/* tmp' + pkg.share_path + 'ajenti/plugins/' + p)
        run('rm tmp' + pkg.share_path + 'ajenti/plugins/' + p + '/info')
        pkg.build('tmp/', 'ajenti-plugin-' + pkgname, ver, base_desc + desc, deps)
    except:
        print 'Skipping plugin ' + p + ': no info file'

print 'Complete'
clean()
