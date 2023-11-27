#!/usr/bin/env python3
import asyncio
import concurrent.futures

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
from gevent import subprocess
import argparse
import shutil
from enum import Enum
from createNewPlugin import clone_plugin

# Ignore ajenti specific python objects
yaml.add_multi_constructor('tag:yaml.org,2002:python/object:', lambda a, b, c: None)

for dep in ['Plugin', 'Binary', 'OptionalPlugin', 'File', 'Module']:
    yaml.add_constructor(f'!{dep}Dependency', lambda a, b: None, Loader=yaml.SafeLoader)


def find_plugins():
    if os.path.exists('__init__.py'):
        yield '.'
    else:
        for dir_path, dn, fn in os.walk('..'):
            for d in sorted(dn):
                dir = os.path.join(dir_path, d)
                if os.path.exists(os.path.join(dir, 'plugin.yml')):
                    yield dir


def run_bower(path, cmdline):
    bower_json = os.path.join(path, 'bower.json')
    bower_rc = os.path.join(path, '.bowerrc')

    if not os.path.exists(bower_json):
        logging.warning('Plugin at %s has no bower.json' % path)
        return

    with open(bower_rc, 'w') as f:
        f.write('{"directory" : "resources/vendor"}')

    if not os.path.exists(os.path.join(path, 'resources/vendor')):
        os.makedirs(os.path.join(path, 'resources/vendor'))

    logging.info('Running bower %s in %s' % (cmdline, path))
    code = subprocess.call('bower -V --allow-root %s' % cmdline, shell=True, cwd=path)
    if code != 0:
        logging.error('Bower failed for %s' % path)
    os.unlink(bower_rc)


def run_npm_install(path):
    package_json = os.path.join(path, 'package.json')

    if not os.path.exists(package_json):
        logging.warning('Plugin at %s has no package.json' % path)
        return

    logging.info('Running npm install in %s' % (path))
    code = subprocess.call('npm --loglevel=verbose install', shell=True, cwd=path)
    if code != 0:
        logging.error('Npm failed for %s' % path)


def run_build(plugin, cache_enabled):
    babel_preset = '/usr/lib/node_modules/babel-preset-es2015'
    if not os.path.isdir(babel_preset):
        babel_preset = 'es2015'

    babel_eh_plugin = '/usr/lib/node_modules/babel-plugin-external-helpers'
    if not os.path.isdir(babel_eh_plugin):
        babel_eh_plugin = 'external-helpers'

    cache_path = '/tmp/.ajenti-resource-cache'
    if not os.path.exists(cache_path):
        os.makedirs(cache_path)

    def get_hash(name):
        return hashlib.sha512(name.encode('utf-8')).hexdigest()

    def get_cached(name):
        if os.path.exists(os.path.join(cache_path, get_hash(name))):
            return open(os.path.join(cache_path, get_hash(name))).read()

    def get_cached_time(name):
        if os.path.exists(os.path.join(cache_path, get_hash(name))):
            return os.stat(os.path.join(cache_path, get_hash(name))).st_mtime

    def set_cached(name, content):
        open(os.path.join(cache_path, get_hash(name)), 'w').write(content.decode())

    resources = yaml.load(open(os.path.join(plugin, 'plugin.yml')), Loader=yaml.SafeLoader)['resources']

    if not resources:
        return
    logging.info('Building resources for %s' % plugin)

    if not os.path.exists(os.path.join(plugin, 'resources/build')):
        os.makedirs(os.path.join(plugin, 'resources/build'))

    all_js = all_vendor_js = all_css = all_vendor_css = ''

    workers = []
    errors = []

    def worker(path, args):
        try:
            set_cached(path, subprocess.check_output(args, stderr=subprocess.STDOUT) + b'\n')
        except subprocess.CalledProcessError as e:
            errors.append({
                'path': path,
                'output': e.output,
            })

    for resource in resources:
        if isinstance(resource, str):
            resource = {'path': resource}

        path = os.path.join(plugin, resource['path'])
        if resource['path'].endswith('.es'):
            if not cache_enabled or not get_cached(path) or get_cached_time(path) < os.stat(path).st_mtime:
                logging.info('Compiling %s' % path)
                workers.append(gevent.spawn(worker, path,
                                            ['babel', '--presets', babel_preset, '--plugins', babel_eh_plugin, path]))
        if resource['path'].endswith('.coffee'):
            if not cache_enabled or not get_cached(path) or get_cached_time(path) < os.stat(path).st_mtime:
                logging.info('Compiling %s' % path)
                workers.append(gevent.spawn(worker, path, ['coffee', '-p', '-c', path]))
        if resource['path'].endswith('.ts'):
            if not cache_enabled or not get_cached(path) or get_cached_time(path) < os.stat(path).st_mtime:
                logging.info('Compiling %s' % path)
                workers.append(gevent.spawn(worker, path, ['tsc', path]))
        if resource['path'].endswith('.less'):
            if not cache_enabled or not get_cached(path) or get_cached_time(path) < os.stat(path).st_mtime:
                logging.info('Compiling %s' % path)
                workers.append(gevent.spawn(worker, path, ['lessc', path]))
        if resource['path'].endswith('.scss'):
            if not cache_enabled or not get_cached(path) or get_cached_time(path) < os.stat(path).st_mtime:
                logging.info('Compiling %s' % path)
                workers.append(gevent.spawn(worker, path, ['sass', path]))

    gevent.joinall(workers)
    if len(errors) > 0:
        logging.error('BUILD FAILED')
        logging.info('  %s error(s):' % len(errors))
        for error in errors:
            logging.error(' * %s' % error['path'])
            for line in error['output'].splitlines():
                logging.warning(line)
        sys.exit(1)

    for resource in resources:
        if isinstance(resource, str):
            resource = {'path': resource}

        path = os.path.join(plugin, resource['path'])

        if 'vendor/' in resource['path'] or 'node_modules/' in resource['path']:
            if resource['path'].endswith('.js'):
                logging.debug('Including %s' % path)
                all_vendor_js += open(path).read() + '\n'
            if resource['path'].endswith('.css'):
                logging.debug('Including %s' % path)
                all_vendor_css += open(path).read() + '\n'
        else:
            if resource['path'].endswith('.coffee'):
                all_js += get_cached(path)
            if resource['path'].endswith('.es'):
                all_js += get_cached(path)
            if resource['path'].endswith('.ts'):
                all_js += get_cached(path)
            if resource['path'].endswith('.js'):
                logging.debug('Including %s' % path)
                all_js += open(path).read() + '\n'
            if resource['path'].endswith('.less'):
                all_css += get_cached(path)
            if resource['path'].endswith('.scss'):
                all_css += get_cached(path)

    content_map = {
        'all.js': all_js,
        'all.css': all_css,
        'all.vendor.js': all_vendor_js,
        'all.vendor.css': all_vendor_css,
    }
    for (k, v) in content_map.items():
        path = os.path.join(plugin, 'resources/build/' + k)
        with open(path, 'w') as f:
            f.write(v)
        os.chmod(path, 0o777)


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


def run_xgettext(plugin):
    locale_path = os.path.join(plugin, 'locale')
    if not os.path.exists(locale_path):
        os.makedirs(locale_path + '/en/LC_MESSAGES')

    pot_path = os.path.join(locale_path, 'app.pot')
    if os.path.exists(pot_path):
        os.unlink(pot_path)

    logging.info('Extracting from %s', plugin)
    logging.info('           into %s', pot_path)

    if subprocess.call(['which', 'xgettext'], stdout=subprocess.PIPE) != 0:
        logging.error('xgettext not found!')
        sys.exit(1)

    if subprocess.call(['which', 'angular-gettext-cli'], stdout=subprocess.PIPE) != 0:
        logging.error('angular-gettext-cli not found (sudo npm -g install angular-gettext-cli)!')
        sys.exit(1)

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

    if subprocess.call(['which', 'msgfmt'], stdout=subprocess.PIPE) != 0:
        logging.error('msgfmt not found!')
        sys.exit(1)

    if subprocess.call(['which', 'angular-gettext-cli'], stdout=subprocess.PIPE) != 0:
        logging.error('angular-gettext-cli not found (sudo npm -g install angular-gettext-cli)!')
        sys.exit(1)

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

def handle_commands(args):
    if args.command == 'new-plugin-minimal':
        new_plugin_minimal(args.name, args.port)
    elif args.command == 'new-plugin-':
        new_plugin(args.name, args.port)
    elif args.command == 'new-plugin-widget':
        new_plugin_widget(args.name, args.port)
    else:
        print("Invalid command")


def modify_port_in_angular_json(directory, project_name, new_port):
    angular_json_path = os.path.join(directory, 'angular.json')
    try:
        with open(angular_json_path, 'r') as file:
            config = json.load(file)

        # Make sure the project exists in the angular.json configuration
        if project_name in config['projects']:
            config['projects'][project_name]['architect']['serve']['options']['port'] = new_port

            with open(angular_json_path, 'w') as file:
                json.dump(config, file, indent=2)
        else:
            print(f"Project {project_name} not found in angular.json")
    except FileNotFoundError:
        print(f"angular.json not found in {directory}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON in {angular_json_path}")


def rename_directory(directory, new_file_name):
    for root, dirs, files in os.walk(directory, topdown=False):
        for file in files:
            old_file_path = os.path.join(root, file)

            if 'basicTemplate' in file:
                file_name = file.replace('basicTemplate', new_file_name)
                new_file_path = os.path.join(root, file_name)

                os.rename(old_file_path, new_file_path)
                print(f"Renamed file: {file} to {file_name}")
            else:
                print(f"Found file: {file}")


class TemplateFolder(Enum):
    MINIMAL = 'minimalTemplate'
    BASIC = 'basicTemplate'
    WIDGET = 'widgetTemplate'


def new_plugin_minimal(name, port):
    path_to_template = os.path.join(os.path.dirname(os.getcwd()), 'plugin-templates', TemplateFolder.MINIMAL.value)
    path_to_generate = os.path.join(os.path.dirname(os.getcwd()), 'plugins-new')
    path_to_new_plugin = os.path.join(os.path.dirname(os.getcwd()), f'plugins-new/{name}')
    clone_plugin(new_folder_path=path_to_new_plugin,
                 new_name=name,
                 old_name=TemplateFolder.MINIMAL.value,
                 template_folder=path_to_template,
                 path_to_plugins_new=path_to_generate,
                 port=port)


def new_plugin(name, port):
    path_to_template = os.path.join(os.path.dirname(os.getcwd()), 'plugin-templates', TemplateFolder.BASIC.value)
    path_to_generate = os.path.join(os.path.dirname(os.getcwd()), 'plugins-new')
    clone_plugin(new_folder_path=path_to_generate,
                 new_name=name,
                 old_name=TemplateFolder.BASIC.value,
                 template_folder=path_to_template,
                 path_to_plugins_new=path_to_generate,
                 port=port
                 )


def new_plugin_widget(name, port):
    path_to_template = os.path.join(os.path.dirname(os.getcwd()), 'plugin-templates', TemplateFolder.WIDGET.value)
    path_to_generate = os.path.join(os.path.dirname(os.getcwd()), 'plugins-new')
    clone_plugin(new_folder_path=path_to_generate,
                 new_name=name,
                 old_name=TemplateFolder.WIDGET.value,
                 template_folder=path_to_template,
                 path_to_plugins_new=path_to_generate,
                 port=port
                 )


def usage():
    print("""
Usage: %s [options]

Plugin commands (these operate on all plugins found within current directory)
    --new-plugin '<some-name>'      - Creates a new plugin boilerplate in current directory
    --run                           - Run Ajenti with plugins from the current directory
    --run-dev                       - Run Ajenti in dev mode with plugins from the current directory
    --log-level '<level>'           - Fix the log level : debug, info, warning or error ( default : debug )
                                      Must be specified before the run command.
    --bower '<cmdline>'             - Run Bower, e.g. --bower install
    --npm                           - Run npm install in each plugin directory discovered
    --build                         - Compile resources
    --rebuild                       - Force recompile resources
    --setuppy '<args>'              - Run a setuptools build
    --bump                          - Bump plugin's version
    --find-outdated                 - Find plugins that have unpublished changes
    --xgettext                      - Extracts localizable strings
    --msgfmt                        - Compiles translated localizable strings
    --new-plugin-minimal '<name>'   - Create a new Ajenti3 plugin without UI
    --new-plugin-widget '<name>'    - Create a new Ajenti3 widget plugin
    """ % sys.argv[0])


if __name__ == '__main__':

    coloredlogs.install(level=logging.DEBUG, show_hostname=False)
    sys.path.insert(0, '..')

    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            '',
            [
                'run',
                'run-dev',
                'run-dev-loglevel=',
                'bower=',
                'npm',
                'build',
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
                'new-plugin-minimal',
                'new-plugin',
                'new-plugin-widget'
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

    parser = argparse.ArgumentParser(description='Ajenti Dev Multitool')

    command_pattern = re.compile(r'--new-plugin-?(\w*)')

    args = sys.argv[1:]
    match = None

    for arg in args:
        match = command_pattern.match(arg)
        if match:
            break

    if match:
        command_name = match.group(1)
        remaining_args = args[args.index(arg) + 1:]

        if command_name == 'minimal':
            parser.add_argument('name', help='Name of the plugin')
            parser.add_argument('-p', '--port', type=int, help='Port number')
        elif command_name == 'widget':
            parser.add_argument('name', help='Name of the plugin')
            parser.add_argument('-p', '--port', type=int, help='Port number')
        elif command_name == '':
            command_name = ''
            parser.add_argument('name', help='Name of the plugin')
            parser.add_argument('-p', '--port', type=int, help='Port number')

        args = parser.parse_args(remaining_args)
        args.command = f'new-plugin-{command_name}'
        handle_commands(args)
        sys.exit(0)

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
        if option == '--bower':
            for plugin in find_plugins():
                run_bower(plugin, argument)
            sys.exit(0)
        if option == '--npm':
            for plugin in find_plugins():
                run_npm_install(plugin)
            sys.exit(0)
        elif option == '--build':
            for plugin in find_plugins():
                run_build(plugin, True)
            logging.info('Resource build complete')
            sys.exit(0)
        elif option == '--rebuild':
            for plugin in find_plugins():
                run_build(plugin, False)
            logging.info('Resource rebuild complete')
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
        elif option == '--log-level':
            cmd += ['--log', argument]
            log_level = True

    usage()
    sys.exit(2)
