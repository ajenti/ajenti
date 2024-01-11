import logging
import os
import shutil
import signal
import subprocess
import sys

serve_processes = []


def ensure_yarn_is_installed():
    if subprocess.call(['which', 'yarn'], stdout=subprocess.PIPE) != 0:
        logging.error('yarn not found!')
        sys.exit(1)


def yarn_install(project_path, remove_node_modules=False):
    print(f'Installing yarn in {project_path}..')
    prev_dir = os.getcwd()
    os.chdir(project_path)

    if remove_node_modules:
        print('Removing node_modules for plugin %s...' % project_path)
        subprocess.run(['rm', '-rf', 'node_modules'])

    subprocess.run(['yarn', 'install'])
    os.chdir(prev_dir)


def yarn_build(project_path):
    prev_dir = os.getcwd()
    os.chdir(project_path)
    subprocess.run(['yarn', 'run', 'build'])
    os.chdir(prev_dir)


def build_plugin_frontend(plugin, clean_mode):
    plugin_frontend_path = os.path.join('plugins-new', plugin, 'frontend')
    yarn_install(plugin_frontend_path, remove_node_modules=clean_mode)
    yarn_build(plugin_frontend_path)


def build_ajenti_lib(clean_mode):
    yarn_install(os.path.join('plugins-new', 'ngx-ajenti'), remove_node_modules=clean_mode)
    yarn_build(os.path.join('plugins-new', 'ngx-ajenti'))


def add_shell_plugin_if_not_exists(plugins):
    if 'shell' not in plugins:
        logging.info('Adding mandatory shell plugin to plugin list.')
        plugins.insert(0, 'shell')


def build_plugins(plugins, clean_mode=False):
    ensure_yarn_is_installed()
    build_ajenti_lib(clean_mode)
    add_shell_plugin_if_not_exists(plugins)
    logging.info(f'Building following plugins: {plugins}')
    for plugin in plugins:
        build_plugin_frontend(plugin, clean_mode)


def prepare_ajenti_lib_for_linking():
    logging.info('Preparing ajenti lib @ngx-ajenti/core for linking..')
    prev_dir = os.getcwd()
    os.chdir(os.path.join('plugins-new', 'ngx-ajenti', 'dist', 'ngx-ajenti'))
    subprocess.run(['yarn', 'unlink'])
    subprocess.run(['yarn', 'link'])
    os.chdir(prev_dir)


def link_ajenti_lib_to_plugin(plugin_frontend_path):
    logging.info(f'Linking plugin {plugin_frontend_path} to @ngx-ajenti/core..')
    prev_dir = os.getcwd()
    os.chdir(plugin_frontend_path)
    subprocess.run(['yarn', 'link', '@ngx-ajenti/core'])
    os.chdir(prev_dir)


def serve_plugin_in_parallel(plugin_frontend_path):
    logging.info(f'Serving plugin {plugin_frontend_path} for development..')
    prev_dir = os.getcwd()
    os.chdir(plugin_frontend_path)

    proc = subprocess.Popen(['yarn', 'start'])
    serve_processes.append(proc)

    os.chdir(prev_dir)


def clear_angular_cache(plugin_frontend_path):
    logging.info(f'Clearing angular cache for {plugin_frontend_path}..')
    angular_cache_path = os.path.join(plugin_frontend_path, '.angular', 'cache')
    if os.path.exists(angular_cache_path):
        subprocess.run(['rm', '-rf', angular_cache_path])


def prepare_angular_proxy_settings(plugin_frontend_path):
    logging.info(f'Preparing angular proxy settings for {plugin_frontend_path}..')
    angular_proxy_settings_path = os.path.join(plugin_frontend_path, 'proxy.conf.json')
    angular_proxy_settings_template_path = os.path.join(plugin_frontend_path, 'proxy.conf.template.json')

    if not os.path.isfile(angular_proxy_settings_path):
        logging.info(f'Copying {angular_proxy_settings_template_path} to {angular_proxy_settings_path}..')
        shutil.copyfile(angular_proxy_settings_template_path, angular_proxy_settings_path)


def serve_plugins(plugins, clean_mode):
    ensure_yarn_is_installed()

    signal.signal(signal.SIGINT, terminate_process_signal_handler)

    build_ajenti_lib(clean_mode)
    prepare_ajenti_lib_for_linking()

    add_shell_plugin_if_not_exists(plugins)
    logging.info(f'Start serving of the following plugins: {plugins}')
    for plugin in plugins:
        plugin_frontend_path = os.path.join('plugins-new', plugin, 'frontend')
        clear_angular_cache(plugin_frontend_path)
        yarn_install(plugin_frontend_path, clean_mode)
        link_ajenti_lib_to_plugin(plugin_frontend_path)
        prepare_angular_proxy_settings(plugin_frontend_path)
        serve_plugin_in_parallel(plugin_frontend_path)

    signal.pause()


def terminate_process_signal_handler(sig, frame):
    print('You pressed Ctrl+C! Terminating all serve processes...')

    for proc in serve_processes:
        try:
            proc.terminate()
            print(f'Process {proc.pid} successfully terminated.')
        except Exception as e:
            logging.error(f'Cannot terminate plugin process {proc.pid}: {e}')
    sys.exit(0)
