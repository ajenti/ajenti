#!/usr/bin/env python
import os
import sys
import subprocess
from lxml import etree


LOCALEDIR = 'ajenti/locale'
LANGUAGES = [x for x in os.listdir(LOCALEDIR) if not '.' in x]

pot_path = os.path.join(LOCALEDIR, 'ajenti.po')

if subprocess.call(['which', 'xgettext']) != 0:
    print 'xgettext app not found'
    sys.exit(0)

for (dirpath, dirnames, filenames) in os.walk('ajenti'):
    for f in filenames:
        path = os.path.join(dirpath, f)
        if f.endswith('.py'):
            print ' :: PY   %s' % path
            subprocess.check_call([
                'xgettext',
                '-c',
                '--from-code=utf-8',
                '--omit-header',
                '-o', pot_path,
                '-j' if os.path.exists(pot_path) else '-dajenti',
                path,
            ])
        if f.endswith('.xml'):
            print ' :: XML  %s' % path
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
                                eval(v, {'_': lambda x: x})
                                msgs.append(v.strip())
                        except:
                            pass
                    for c in n:
                        traverse(c)
                traverse(xml)

                fake_content = ''.join('gettext("%s");\n' % msg for msg in msgs)
                fake_content = 'void main() { ' + fake_content + ' }'

                open(path, 'w').write(fake_content)
                subprocess.check_call([
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

for lang in LANGUAGES:
    po_dir = os.path.join(LOCALEDIR, lang, 'LC_MESSAGES')
    po_path = os.path.join(po_dir, 'ajenti.po')
    mo_path = os.path.join(po_dir, 'ajenti.mo')

    if not os.path.exists(po_dir):
        os.makedirs(po_dir)

    """
    print ' :: Merging %s' % lang
    subprocess.check_call([
        'msgmerge',
        '-U',
        '--backup=off',
        po_path,
        pot_path,
    ])
    """

    print ' :: Compiling %s' % lang
    subprocess.check_call([
        'msgfmt',
        po_path,
        '-v',
        '-o', mo_path
    ])
