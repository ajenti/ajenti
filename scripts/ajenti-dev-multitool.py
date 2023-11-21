#!/usr/bin/env python3
import coloredlogs
import getopt
import gevent
import hashlib
import json
import logging
import os
import re
import shutil
import sys
import tempfile
import time
import yaml
from distutils import util
from gevent import subprocess

# Ignore ajenti specific python objects
yaml.add_multi_constructor('tag:yaml.org,2002:python/object:', lambda a, b, c: None)

for dep in ['Plugin', 'Binary', 'OptionalPlugin', 'File', 'Module']:
    yaml.add_constructor(f'!{dep}Dependency', lambda a, b: None, Loader=yaml.SafeLoader)


def find_plugins():
    if is_plugin_directory('.'):
        yield '.'
    else:
        for root, dirs, files in os.walk('.'):
            for directory_name in sorted(dirs):
                directory_path = os.path.join(root, directory_name)
                is_ignored_path = ('/node_modules' in directory_path) or ('/locale' in directory_path)
                if is_ignored_path:
                    continue
                if is_plugin_directory(directory_path):
                    yield directory_path


def is_plugin_directory(directory_path):
    contains_plugin_yml = os.path.exists(os.path.join(directory_path, 'plugin.yml'))
    is_obsolete_plugin = '/plugins/' in directory_path

    if contains_plugin_yml:
        if not is_obsolete_plugin:
            return True
        else:
            logging.info('Ignoring obsolete plugin: ' + directory_path)
    return False


def get_full_path_from_repo_root(path_from_repo_root):
    return os.path.join(get_repo_root_full_path(), path_from_repo_root)


def get_repo_root_full_path():

    checked_folder_levels = 0
    current_directory = os.getcwd()

    while not is_repo_root_directory(current_directory):
        current_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
        checked_folder_levels += 1
        if checked_folder_levels > 10:
            logging.error("Can't find the root directory of the Ajenti repo")
            sys.exit(1)

    return current_directory


def is_repo_root_directory(directory_path):
    contains_ajenti_panel = os.path.exists(os.path.join(directory_path, 'ajenti-panel'))
    contains_ajenti_core = os.path.exists(os.path.join(directory_path, 'ajenti-core'))

    return contains_ajenti_panel and contains_ajenti_core


def is_yarn_installed():
    exit_code = subprocess.call('yarn --version &> /dev/null', shell=True)
    if exit_code == 0:
        return True
    return False


def build_ngxajenti():
    path = get_full_path_from_repo_root('plugins-new/ngx-ajenti')

    logging.info('@angular/cli: Setting up yarn as the default package manager')
    exit_code = subprocess.call('ng config -g cli.packageManager yarn', shell=True, cwd=path)
    if exit_code != 0:
        logging.error('Failed to set the yarn as the default package manager.')
        return

    is_yarn_install_successful = run_yarn_install(path)
    if not is_yarn_install_successful:
        return

    logging.info('Running yarn build in %s' % path)
    exit_code = subprocess.call('yarn run build', shell=True, cwd=path)
    if exit_code != 0:
        logging.error('Failed running yarn build for %s' % path)
        return


def run_yarn_install(path):
    logging.info('Running yarn install in %s' % path)
    exit_code = subprocess.call('yarn install', shell=True, cwd=path)
    if exit_code != 0:
        logging.error('Failed running yarn install in %s' % path)
        return False
    return True


def setup_angular_dev_tools_proxy(path_to_plugin):
    plugin_frontend_path = os.path.abspath(os.path.join(path_to_plugin, 'frontend'))
    proxy_file = os.path.join(plugin_frontend_path, 'proxy.conf.json')
    if not os.path.exists(proxy_file):
        proxy_file_template = os.path.join(plugin_frontend_path, 'proxy.conf.template.json')
        logging.info('Creating proxy file:' + proxy_file)
        logging.info('! INFO ! Make sure to configure the proxy file. See the plugins-new/README.txt for more details.')
        shutil.copyfile(proxy_file_template, proxy_file)


def build_plugin_frontend(path_to_plugin):
    plugin_frontend_path = os.path.abspath(os.path.join(path_to_plugin, 'frontend'))

    if not os.path.exists(plugin_frontend_path):
        return

    package_json = os.path.join(plugin_frontend_path, 'package.json')

    if not os.path.exists(package_json):
        logging.warning('Plugin at %s has no package.json' % plugin_frontend_path)
        return

    logging.info('Creating Symbolic link to  "@ngx-ajenti/core" in %s' % plugin_frontend_path)
    subprocess.call('mkdir -p node_modules/@ngx-ajenti', shell=True, cwd=plugin_frontend_path)
    exit_code = subprocess.call('ln -nsf ../../../../ngx-ajenti/dist/ngx-ajenti node_modules/@ngx-ajenti/core',
                                shell=True, cwd=plugin_frontend_path)
    if exit_code != 0:
        logging.error('Creation of Symbolic link failed for %s' % plugin_frontend_path)
        return

    is_yarn_install_successful = run_yarn_install(plugin_frontend_path)
    if not is_yarn_install_successful:
        return


def run_setuptools(plugin, cmd):
    info = yaml.load(open(os.path.join(plugin, 'plugin.yml')), Loader=yaml.SafeLoader)
    info['pypi_name'] = info['name']
    if 'demo_' in plugin:
        return
    workspace = tempfile.mkdtemp()
    logging.info('Running setup.py for %s', plugin)
    logging.debug('Working under %s' % workspace)
    workspace_plugin = os.path.join(workspace, 'ajenti_plugin_%s' % info['name'])

    dist = os.path.join(plugin, 'dist')
    if os.path.exists(dist):
        shutil.rmtree(dist)

    shutil.copytree(plugin, workspace_plugin)
    shutil.copy(os.path.join(plugin, 'requirements.txt'), workspace)

    setuppy = '''
#!/usr/bin/env python3
from setuptools import setup, find_packages

import os

__requires = [dep.split('#')[0].strip() for dep in filter(None, open('requirements.txt').read().splitlines())] 

setup(
    name='ajenti.plugin.%(pypi_name)s',
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

    open(os.path.join(workspace, 'README'), 'w').close()

    manifest = '''
recursive-include ajenti_plugin_%(name)s * *.*
recursive-exclude ajenti_plugin_%(name)s *.pyc
include ajenti_plugin_%(name)s/plugin.yml
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

    logging.info('  -> setup.py %s', cmd)
    try:
        subprocess.check_output('python3 setup.py %s' % cmd, cwd=workspace, shell=True)
    except subprocess.CalledProcessError as e:
        logging.error('Output: %s', e.output)
        logging.error('setup.py failed for %s, code %s', plugin, e.returncode)
        return

    dist = os.path.join(workspace, 'dist')
    sdist = os.path.join(plugin, 'dist')
    if os.path.exists(sdist):
        shutil.rmtree(sdist)
    if os.path.exists(dist):
        shutil.copytree(dist, sdist)

    shutil.rmtree(workspace)

    if 'upload' in cmd.split():
        open(os.path.join(plugin, '.last-upload'), 'w').write(str(time.time()))

    logging.info('setup.py has finished')


def run_bump(plugin):
    path = os.path.join(plugin, 'plugin.yml')
    output = ''
    bumped = False
    for l in open(path).read().splitlines():
        if l.startswith('version:'):
            prefix, counter = l.rsplit('.', 1)
            counter = counter.rstrip("'")
            counter = str(int(counter) + 1)
            l = prefix + '.' + counter
            if "'" in prefix:
                l += "'"
            bumped = True
        output += l + '\n'
    if bumped:
        with open(path, 'w') as f:
            f.write(output)
        logging.info('Bumped %s to %s.%s', plugin, prefix.split(':')[1].strip(" '"), counter)
    else:
        logging.warning('Could not find version info for %s', plugin)


def run_find_outdated(plugin):
    if 'demo_' in plugin:
        return
    last_upload = 0
    last_file = os.path.join(plugin, '.last-upload')
    if os.path.exists(last_file):
        last_upload = float(open(last_file).read())

    last_changed = 0
    for d, dn, fn in os.walk(plugin):
        if d.endswith('/dist'):
            continue
        if d.endswith('/resources/build'):
            continue
        for f in fn:
            if os.path.splitext(f)[-1] in ['.pyc']:
                continue
            if os.stat(os.path.join(d, f)).st_mtime > last_upload + 10:
                logging.info('*** %s/%s', d, f)
            last_changed = max(last_changed, os.stat(os.path.join(d, f)).st_mtime)

    if last_changed > last_upload + 10:
        logging.warning('Plugin %s has unpublished changes', plugin)
        return True


def throw_error_if_not_installed(package_name, error_message):
    if subprocess.call(['which', package_name], stdout=subprocess.PIPE) != 0:
        logging.error(error_message)
        sys.exit(1)

def run_xgettext(plugin):
    locale_path = os.path.join(plugin, 'locale')
    if not os.path.exists(locale_path):
        os.makedirs(locale_path + '/en/LC_MESSAGES')

    pot_path = os.path.join(locale_path, 'app.pot')
    if os.path.exists(pot_path):
        os.unlink(pot_path)

    logging.info('Extracting from %s', plugin)
    logging.info('           into %s', pot_path)

    throw_error_if_not_installed('xgettext', 'xgettext not found!')
    throw_error_if_not_installed('angular-gettext-cli',
                                 'angular-gettext-cli not found (sudo yarn global add angular-gettext-cli)!')

    subprocess.check_call([
        'angular-gettext-cli',
        '--files', '%s/**/*.html' % plugin,
        '--dest', pot_path,
        '--marker-name', 'i18n',
    ])

    for (dirpath, dirnames, filenames) in os.walk(plugin, followlinks=True):
        if 'vendor' in dirpath or 'build' in dirpath or 'node_modules' in dirpath:
            continue
        for f in filenames:
            path = os.path.join(dirpath, f)
            if f.endswith(('.coffee', '.js', '.ts', '.es')):
                logging.info(' -> (js) %s' % path)
                subprocess.check_call([
                    'xgettext',
                    '--from-code', 'utf-8',
                    '-c', '-d', 'app',
                    '-L', 'javascript',
                    '--keyword=gettext',
                    '-o', pot_path,
                    '-j', path,
                ])
            if f.endswith('.py'):
                logging.info(' -> (py) %s' % path)
                subprocess.check_call([
                    'xgettext',
                    '--from-code', 'utf-8',
                    '-c', '-d', 'app',
                    '-o', pot_path,
                    '-j', path,
                ])

    for dir in os.listdir(locale_path):
        path = os.path.join(locale_path, dir, 'LC_MESSAGES')
        if os.path.isdir(path):
            logging.info(' :: processing %s' % dir)
            po_path = os.path.join(path, 'app.po')
            if os.path.exists(po_path):
                subprocess.check_call([
                    'msgmerge',
                    '-U',
                    po_path, pot_path,
                ])
            else:
                with open(po_path, 'w') as f:
                    f.write(open(pot_path).read())


def run_push_crowdin(plugins, add=False):
    dir = tempfile.mkdtemp()
    logging.info('Working in %s' % dir)
    for plugin in plugins:
        locale_path = os.path.join(plugin, 'locale')
        pot_path = os.path.join(locale_path, 'app.pot')
        if os.path.exists(pot_path):
            logging.info('Copying %s', pot_path)
            with open(os.path.join(dir, os.path.split(plugin)[1] + '.po'), 'w') as f:
                f.write(open(pot_path).read())

    try:
        crowdin_key = open('.crowdin.key').read().strip().split('\n')
        if len(crowdin_key) == 2:
            project_name = crowdin_key[1]
        else:
            project_name = 'ajenti'
        key = crowdin_key[0]
    except Exception as e:
        logging.error('Could not read ".crowdin.key": %s', e)
        sys.exit(1)

    for file in os.listdir(dir):
        logging.info(' :: uploading %s' % file)
        subprocess.check_call([
            'curl', '-F', 'files[/2.0/%s]=@%s' % (
                file,
                os.path.join(dir, file),
            ),
            'https://api.crowdin.com/api/project/%s/%s?key=%s' % (
                project_name,
                'add-file' if add else 'update-file',
                key
            )
        ])

    shutil.rmtree(dir)


def run_pull_crowdin(plugins):
    try:
        crowdin_key = open('.crowdin.key').read().strip().split('\n')
        if len(crowdin_key) == 2:
            project_name = crowdin_key[1]
        else:
            project_name = 'ajenti'
        key = crowdin_key[0]
    except Exception as e:
        logging.error('Could not read ".crowdin.key": %s', e)
        sys.exit(1)

    map = dict((os.path.split(p)[1], p) for p in plugins)
    dir = tempfile.mkdtemp()
    logging.info('Working in %s' % dir)

    logging.info('Requesting build')
    subprocess.check_call([
        'curl', 'https://api.crowdin.com/api/project/%s/export?key=%s' % (project_name, key)
    ])

    logging.info('Downloading')
    zip_path = os.path.join(dir, 'all.zip')
    subprocess.check_call([
        'wget', 'https://api.crowdin.com/api/project/%s/download/all.zip?key=%s' % (project_name, key),
        '-O', zip_path
    ])

    subprocess.check_call([
        'unzip', 'all.zip'
    ], cwd=dir)

    os.unlink(zip_path)

    for lang in os.listdir(dir):
        if lang == 'ajenti':
            continue
        logging.info(' -> processing %s', lang)
        for name, plugin in map.items():
            zip_po_path = os.path.join(dir, lang, '2.0', name + '.po')
            if os.path.exists(zip_po_path):
                locale_path = os.path.join(plugin, 'locale', lang, 'LC_MESSAGES')
                if not os.path.exists(locale_path):
                    os.makedirs(locale_path)
                po_path = os.path.join(locale_path, 'app.po')
                with open(po_path, 'w') as f:
                    f.write(open(zip_po_path).read())

    shutil.rmtree(dir)


def run_msgfmt(plugin):
    locale_path = os.path.join(plugin, 'locale')
    if not os.path.exists(locale_path):
        return

    logging.info('Compiling in %s', locale_path)

    throw_error_if_not_installed('msgfmt', 'msgfmt not found!')
    throw_error_if_not_installed('angular-gettext-cli',
                                 'angular-gettext-cli not found (sudo yarn global add angular-gettext-cli)!')

    for lang in os.listdir(locale_path):
        if lang in ['app.pot', 'en']:
            continue

        po_path = os.path.join(locale_path, lang, 'LC_MESSAGES', 'app.po')
        js_path = os.path.join(locale_path, lang, 'LC_MESSAGES', 'app.js')

        '''
        subprocess.check_call([
            'msgfmt',
            po_path,
            '-option',
            os.path.join(locale_path, lang, 'LC_MESSAGES', 'app.mo'),
        ])
        '''

        js_locale = {}
        msgid = None
        for line in open(po_path):
            if line.startswith('msgid'):
                msgid = line.split(None, 1)[1].strip().strip('"')
            if line.startswith('msgstr'):
                msgstr = line.split(None, 1)[1].strip().strip('"')
                js_locale[msgid] = msgstr

        with open(js_path, 'w') as f:
            f.write(json.dumps(js_locale))

def new_plugin(name):
    words = filter(None, re.split(r'[-\s]+', name))
    words = [re.sub(r'[^\w]', '', x).lower() for x in words]
    plugin_name = '_'.join(words)
    plugin_dash_name = '-'.join(words)
    pluginName = words[0] + ''.join([(x[0].upper() + x[1:]) for x in words[1:]])
    PluginName = ''.join([(x[0].upper() + x[1:]) for x in words])
    Plugin_Name = ' '.join([(x[0].upper() + x[1:]) for x in words])

    logging.info('Using plugin name: %s', plugin_name)

    logging.info('Downloading plugin template')
    subprocess.check_call(['wget', 'https://github.com/ajenti/plugin-template/archive/master.zip'])
    subprocess.check_call(['unzip', 'master.zip'])
    os.unlink('master.zip')
    os.rename('plugin-template-master', plugin_name)

    logging.info('Renaming plugin')
    for dir_path, dirs, files in os.walk(plugin_name):
        for file_name in files:
            path = os.path.join(dir_path, file_name)
            content = open(path).read()
            content = content.replace('MyPlugin', PluginName)
            content = content.replace('My Plugin', Plugin_Name)
            content = content.replace('myPlugin', pluginName)
            content = content.replace('my_plugin', plugin_name)
            content = content.replace('my-plugin', plugin_dash_name)
            with open(path, 'w') as f:
                f.write(content)

    logging.info('Plugin created under ./%s/', plugin_name)


def usage():
    print("""
Usage: %s [options]

Plugin commands (these operate on all plugins found within current directory)
    --new-plugin '<some-name>'      - Creates a new plugin boilerplate in current directory
    --run                           - Run Ajenti with plugins from the current directory
    --run-dev                       - Run Ajenti in dev mode with plugins from the current directory
    --log-level '<level>'           - Fix the log level : debug, info, warning or error ( default : debug )
                                      Must be specified before the run command.
    --build-frontend                - Builds the frontends in all plugins
    --setuppy '<args>'              - Run a setuptools build
    --bump                          - Bump plugin's version
    --find-outdated                 - Find plugins that have unpublished changes
    --xgettext                      - Extracts localizable strings
    --msgfmt                        - Compiles translated localizable strings
    """ % sys.argv[0])


if __name__ == '__main__':
    coloredlogs.install(level=logging.DEBUG, show_hostname=False)
    sys.path.insert(0, '.')

    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            '',
            [
                'run',
                'run-dev',
                'run-dev-loglevel=',
                'build-frontend',
                'rebuild',
                'setuppy=',
                'bump',
                'find-outdated',
                'xgettext',
                'msgfmt',
                'add-crowdin',
                'push-crowdin',
                'pull-crowdin',
                'new-plugin=',
                'log-level=',
            ]
        )
    except getopt.GetoptError as e:
        print(str(e))
        usage()
        sys.exit(2)

    cmd = [
            'ajenti-panel',
            '--autologin', '--stock-plugins', '--plugins', '.'
    ]
    log_level = False

    for option, argument in opts:
        if option.startswith('--run'):
            if option == '--run-dev':
                if not log_level:
                    cmd += ['-v', '--dev']
                else:
                    # dev option must be inserted before log-level
                    cmd.insert(-2, '--dev')
            try:
                subprocess.call(cmd)
            except KeyboardInterrupt:
                pass
            sys.exit(0)

        if option == '--build-frontend':
            logging.info('Starting to build the frontends of all plugins found in the current directory and bellow..')

            if not is_yarn_installed():
                logging.error('Yarn is not installed!')
                sys.exit(1)

            build_ngxajenti()

            for plugin_path in find_plugins():
                setup_angular_dev_tools_proxy(plugin_path)
                build_plugin_frontend(plugin_path)

            logging.info('Frontends of all found plugins were successfully built.')
            sys.exit(0)

        elif option == '--setuppy':
            for plugin in find_plugins():
                run_setuptools(plugin, argument)
            sys.exit(0)
        elif option == '--bump':
            for plugin in find_plugins():
                run_bump(plugin)
            sys.exit(0)
        elif option == '--find-outdated':
            found = 0
            for plugin in find_plugins():
                if run_find_outdated(plugin):
                    found += 1
            logging.info('Scan complete, %s updated plugin(s) found', found)
            sys.exit(0)
        elif option == '--xgettext':
            for plugin in find_plugins():
                run_xgettext(plugin)
            sys.exit(0)
        elif option == '--msgfmt':
            for plugin in find_plugins():
                run_msgfmt(plugin)
            sys.exit(0)
        elif option == '--add-crowdin':
            run_push_crowdin(list(find_plugins()), add=True)
            sys.exit(0)
        elif option == '--push-crowdin':
            run_push_crowdin(list(find_plugins()))
            sys.exit(0)
        elif option == '--pull-crowdin':
            run_pull_crowdin(list(find_plugins()))
            sys.exit(0)
        elif option == '--new-plugin':
            new_plugin(argument)
            sys.exit(0)
        elif option == '--log-level':
            cmd += ['--log', argument]
            log_level = True

    usage()
    sys.exit(2)