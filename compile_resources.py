#!/usr/bin/env python
import subprocess
import shutil
import glob
import os
import re
import sys
import gevent

try:
    from gevent import subprocess
except:
    import subprocess

import uuid
import threading

import logging
import ajenti.compat
import ajenti.log


def check_output(*args, **kwargs):
    try:
        return subprocess.check_output(*args, **kwargs)
    except Exception, e:
        logging.error('Call failed')
        logging.error(' '.join(args[0]))
        logging.error(str(e))
        sys.exit(0)


ajenti.log.init()


def dirname():
    return 'tmp/' + str(uuid.uuid4())

def compile_coffeescript(inpath):
    outpath = '%s.c.js' % inpath

    if os.path.exists(outpath) and os.stat(outpath).st_mtime > os.stat(inpath).st_mtime:
        logging.info('Skipping %s' % inpath)
        return

    logging.info('Compiling CoffeeScript: %s' % inpath)

    d = dirname()
    check_output('coffee -o %s -c "%s"' % (d, inpath), shell=True)
    shutil.move(glob.glob('./%s/*.js' % d)[0], outpath)
    shutil.rmtree(d)


def compile_less(inpath):
    outpath = '%s.c.css' % inpath

    if os.path.exists(outpath) and os.stat(outpath).st_mtime > os.stat(inpath).st_mtime:
        logging.info('Skipping %s' % inpath)
        #return

    logging.info('Compiling LESS %s' % inpath)
    out = check_output('lessc "%s" "%s"' % (inpath, outpath), shell=True)
    if out:
        logging.error(out)
    #print subprocess.check_output('recess --compile "%s" > "%s"' % (inpath, outpath), shell=True)

compilers = {
    r'.+\.coffee$': compile_coffeescript,
    r'.+[^i]\.less$': compile_less,
}



greenlets = []

def traverse(fx):
    plugins_path = './ajenti/plugins'
    for plugin in os.listdir(plugins_path):
        path = os.path.join(plugins_path, plugin, 'content')
        if os.path.exists(path):
            for (dp, dn, fn) in os.walk(path):
                for name in fn:
                    file_path = os.path.join(dp, name)
                    greenlets.append(gevent.spawn(fx, file_path))

    done = 0
    done_gls = []
    length = 40
    total = len(greenlets)
    print

    while True:
        for gl in greenlets:
            if gl.ready() and not gl in done_gls:
                done_gls.append(gl)
                done += 1
                dots = int(1.0 * length * done / total)
                sys.stdout.write('\r%3i/%3i [' % (done, total) + '.' * dots + ' ' * (length - dots) + ']')
                sys.stdout.flush()
        gevent.sleep(0.1)
        if done == total:
            print
            break



def compile(file_path):
    for pattern in compilers:
        if re.match(pattern, file_path):
            compilers[pattern](file_path)



if not os.path.exists('tmp'):
    os.mkdir('tmp')

greenlets = []
traverse(compile)
