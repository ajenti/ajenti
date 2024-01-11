import os
import yaml
import tempfile
import logging
import shutil
import subprocess


# TODO
# Integrate to multitool
# Customize exclude/include list
# Check dev mode on production server

# Ignore ajenti specific python objects
yaml.add_multi_constructor('tag:yaml.org,2002:python/object:', lambda a, b, c: None)

for dep in ['Plugin', 'Binary', 'OptionalPlugin', 'File', 'Module']:
    yaml.add_constructor(f'!{dep}Dependency', lambda a, b: None, Loader=yaml.SafeLoader)

def clear_builds():
    shutil.rmtree(os.path.join('debian', 'build'))
    os.makedirs(os.path.join('debian', 'build'))

def build_panel_deb():
    fpm_cmd = [
        '/usr/local/bin/fpm',
        '-s', 'python',
        '-t', 'deb',
        '--python-bin', 'python3',
        '-p', 'debian/build/ajenti3_VERSION_ARCH.deb',
        '-x', '"*.pyc"',
        '-x', '"*/__pycache__"',
        '--no-auto-depends',
        '-d', 'build-essential',
        '-d', 'python3-pip',
        '-d', 'python3-dev',
        '-d', 'python3-lxml',
        '-d', 'python3-dbus',
        '-d', 'python3-augeas',
        '-d', 'libssl-dev',
        '-d', 'python3-apt',
        '-d', 'ntpdate',
        '--maintainer', 'arnaud@linuxmuster.net',
        '--deb-changelog', 'CHANGELOG.txt',
        '--config-files', 'etc/ajenti/requirements.txt',
        '--after-install', 'debian/scripts/postinstall.sh',
        '--deb-systemd', 'debian/systemd/ajenti3.service',
        '--deb-systemd-enable',
        '--deb-systemd-auto-start',
        'ajenti-panel'
    ]

    os.makedirs('etc/ajenti')
    shutil.copy(os.path.join('ajenti-core', 'requirements.txt'), 'etc/ajenti')

    subprocess.check_call(fpm_cmd)

    shutil.rmtree('etc')

def build_plugin_deb(plugin):
    plugin_path = os.path.join('plugins-new', plugin)
    info = yaml.load(open(os.path.join(plugin_path, 'plugin.yml')), Loader=yaml.SafeLoader)
    info['pypi_name'] = info['name']
    if 'demo_' in plugin:
        return
    workspace = tempfile.mkdtemp()
    logging.info('Preparing Debian package for %s', plugin)
    logging.debug('Working under %s' % workspace)
    workspace_plugin = os.path.join(workspace, 'ajenti3_plugin_%s' % info['name'])

    dist = os.path.join(plugin, 'dist')
    if os.path.exists(dist):
        shutil.rmtree(dist)

    shutil.copytree(plugin_path, workspace_plugin, ignore=shutil.ignore_patterns('.angular', 'node_modules'))
    shutil.copy(os.path.join(plugin_path, 'backend', 'requirements.txt'), workspace)

    setuppy = '''
#!/usr/bin/env python3
from setuptools import setup, find_packages

import os

__requires = [dep.split('#')[0].strip() for dep in filter(None, open('requirements.txt').read().splitlines())] 

setup(
    name='ajenti3.plugin.%(pypi_name)s',
    version='%(version)s',
    python_requires='>=3',
    install_requires=__requires,
    description='%(title)s',
    long_description='A %(title)s plugin for Ajenti panel',
    author='%(author)s',
    author_email='%(email)s',
    url='%(url)s',
    packages=find_packages(),
    include_package_data=True,
)
    '''.strip() % info
    with open(os.path.join(workspace, 'setup.py'), 'w') as f:
        f.write(setuppy)

    manifest = '''
recursive-include ajenti3_plugin_%(name)s * *.*
recursive-exclude ajenti3_plugin_%(name)s *.pyc
include ajenti3_plugin_%(name)s/plugin.yml
include MANIFEST.in
include requirements.txt
    ''' % info
    with open(os.path.join(workspace, 'MANIFEST.in'), 'w') as f:
        f.write(manifest)

    if 'pre_build' in info:
        logging.info('  -> running pre-build script')
        f = tempfile.NamedTemporaryFile(delete=False, mode='w')
        try:
            f.write(info['pre_build'])
            f.close()
            subprocess.check_call(['sh', f.name], cwd=workspace_plugin)
        finally:
            os.unlink(f.name)

    fpm_cmd = [
        '/usr/local/bin/fpm',
        '-s', 'python',
	    '-t', 'deb',
	    '--python-bin', 'python3',
	    '-p', f'debian/build/ajenti3_plugin_{info["pypi_name"]}_VERSION_ARCH.deb',
	    '-x', '"*.pyc"',
	    '-x', '"*/__pycache__"',
	    '--no-auto-depends',
	    '--maintainer', info['email'],
	    '--deb-changelog', 'CHANGELOG.txt',
	    workspace,
    ]

    subprocess.check_call(fpm_cmd)
    shutil.rmtree(workspace)

# This is wrong, only for migration phase
clear_builds()
build_panel_deb()

for plugin in ['fstab', 'dashboard', 'traffic', 'session_list', 'shell']:
    build_plugin_deb(plugin)