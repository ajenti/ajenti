#!/usr/bin/env python
import os
import sys
import subprocess
from lxml import etree

import logging
import ajenti.log


def check_call(*args):
    try:
        subprocess.call(*args)
    except Exception as e:
        logging.error('Call failed')
        logging.error(' '.join(args[0]))
        logging.error(str(e))


ajenti.log.init()

LOCALEDIR = 'ajenti/locales'
LANGUAGES = [x for x in os.listdir(LOCALEDIR) if not '.' in x]

pot_path = os.path.join(LOCALEDIR, 'ajenti.po')

if len(sys.argv) != 2:
    logging.error('Usage: ./make_messages.py [extract|compile]')
    sys.exit(1)

if subprocess.call(['which', 'xgettext']) != 0:
    logging.error('xgettext app not found')
    sys.exit(0)

if sys.argv[1] == 'extract':
    os.unlink(pot_path)
    for (dirpath, dirnames, filenames) in os.walk('ajenti', followlinks=True):
        if '/custom_' in dirpath:
            continue
        if '/elements' in dirpath:
            continue
        for f in filenames:
            path = os.path.join(dirpath, f)
            if f.endswith('.py'):
                logging.info('Extracting from %s' % path)
                check_call([
                    'xgettext',
                    '-c',
                    '--from-code=utf-8',
                    '--omit-header',
                    '-o', pot_path,
                    '-j' if os.path.exists(pot_path) else '-dajenti',
                    path,
                ])
            if f.endswith('.xml'):
                logging.info('Extracting from %s' % path)
                content = open(path).read()
                xml = etree.fromstring('<xml xmlns:bind="bind" xmlns:binder="binder">' + content + '</xml>')
                try:
                    msgs = []

                    def traverse(n):
                        for k, v in n.items():
                            if v.startswith('{') and v.endswith('}'):
                                msgs.append(v[1:-1])
                            try:
                                if "_('" in v:
                                    eval(v, {'_': msgs.append})
                            except:
                                pass
                        for c in n:
                            traverse(c)
                    traverse(xml)

                    fake_content = ''.join('gettext("%s");\n' % msg for msg in msgs)
                    fake_content = 'void main() { ' + fake_content + ' }'

                    open(path, 'w').write(fake_content)
                    check_call([
                        'xgettext',
                        '-C',
                        '--from-code=utf-8',
                        '--omit-header',
                        '-o', pot_path,
                        '-j' if os.path.exists(pot_path) else '-dajenti',
                        path,
                    ])
                finally:
                    open(path, 'w').write(content)

if sys.argv[1] == 'compile':
    for lang in LANGUAGES:
        po_dir = os.path.join(LOCALEDIR, lang, 'LC_MESSAGES')
        po_path = os.path.join(po_dir, 'ajenti.po')
        mo_path = os.path.join(po_dir, 'ajenti.mo')

        if not os.path.exists(po_dir):
            os.makedirs(po_dir)

        logging.info('Compiling %s' % lang)
        check_call([
            'msgfmt',
            po_path,
            '-v',
            '-o', mo_path
        ])
