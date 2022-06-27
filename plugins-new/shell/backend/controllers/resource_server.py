import json
import logging
import os
from jadi import component

import aj
from aj.api.http import get, HttpPlugin
from aj.plugins import PluginManager

from aj.api.endpoint import endpoint


@component(HttpPlugin)
class ResourcesHandler(HttpPlugin):
    def __init__(self, http_context):
        self.cache = {}
        self.use_cache = not aj.debug
        self.mgr = PluginManager.get(aj.context)

    def __wrap_js(self, name, js):
        """
        Wrap the content with exception handler.

        :param name: File path
        :type name: string
        :param js: Content of the resource
        :type js: string
        :return: Wrapped content
        :rtype: string
        """

        return f'''
                    try {{
                        {js}
                    }} catch (err) {{
                        console.warn('Plugin load error:');
                        console.warn(' * {name}');
                        console.error('  ', err);
                    }}
                '''

    @get(r'/resources/all\.(?P<type>.+)')
    @endpoint(page=True, auth=False)
    def handle_build(self, http_context, type=None):
        if self.use_cache and type in self.cache:
            content = self.cache[type]
        else:
            content = ''
            if type in ['js', 'css', 'vendor.js', 'vendor.css']:
                for plugin in self.mgr:
                    try:
                        requires_angular_build = self.mgr[plugin]['info']['requires-angular-build']
                    except KeyError:
                        requires_angular_build = False

                    frontend_output_path = 'resources/build/'

                    if type == 'js' and requires_angular_build:
                        paths = (
                            'polyfills.js',
                            'main.js'
                        )

                        for path in paths:
                            logging.info(f'path before is: {path}')
                            path = self.mgr.get_content_path(plugin, f'{frontend_output_path}{path}')
                            logging.info(f'path after is: {path}')
                            if os.path.exists(path):
                                file_content = open(path, encoding="utf-8").read()
                                content += self.__wrap_js(path, file_content)
                    else:
                        path = self.mgr.get_content_path(plugin, f'{frontend_output_path}all.{type}')

                        if os.path.exists(path):
                            file_content = open(path, encoding="utf-8").read()
                            if type == 'js':
                                file_content = self.__wrap_js(path, file_content)
                            content += file_content
            if type == 'init.js':
                ng_modules = {}
                for plugin in self.mgr:
                    for resource in self.mgr[plugin]['info']['resources']:
                        if resource['path'].startswith('ng:'):
                            ng_modules.setdefault(plugin, []).append(resource['path'].split(':')[-1])
                content = f'''
                    window.__ngModules = {json.dumps(ng_modules)};
                '''
            if type == 'locale.json':
                lang = http_context.query.get('lang', None)
                if lang:
                    js_locale = {}
                    for plugin in self.mgr:
                        locale_dir = self.mgr.get_content_path(plugin, 'locale')
                        js_path = os.path.join(locale_dir, lang, 'LC_MESSAGES', 'app.js')
                        if os.path.exists(js_path):
                            js_locale.update(json.load(open(js_path)))
                    content = json.dumps(js_locale)
                else:
                    content = ''
            if type == 'partials.js':
                content = '''
                    angular.module("core.templates", []);
                    angular.module("core.templates").run(
                        ["$templateCache", function($templateCache) {
                '''
                for plugin in self.mgr:
                    for resource in self.mgr[plugin]['info']['resources']:
                        path = resource['path']
                        name = resource.get('overrides', f'{plugin}:{path}')

                        if name.endswith('.html'):
                            path = self.mgr.get_content_path(plugin, path)
                            if os.path.exists(path):
                                template = open(path).read()
                                content += f'''
                                      $templateCache.put("{http_context.prefix}/{name}", {json.dumps(template)});
                                '''
                content += '''
                    }]);
                '''

            self.cache[type] = content

        http_context.add_header('Content-Type', {
            'css': 'text/css',
            'js': 'application/javascript; charset=utf-8',
            'vendor.css': 'text/css',
            'vendor.js': 'application/javascript; charset=utf-8',
            'init.js': 'application/javascript; charset=utf-8',
            'locale.json': 'application/json; charset=utf-8',
            'partials.js': 'application/javascript; charset=utf-8',
        }[type])
        http_context.respond_ok()

        return http_context.gzip(content=content.encode('utf-8'))

    @get(r'/resources/(?P<plugin>\w+)/(?P<path>.+)')
    @endpoint(page=True, auth=False)
    def handle_file(self, http_context, plugin=None, path=None):
        if '..' in path:
            return http_context.respond_not_found()
        return http_context.file(PluginManager.get(aj.context).get_content_path(plugin, path))

    @get('/resources/global.constants.js')
    @endpoint(page=True, auth=False)
    def handle_global_constants(self, http_context):
        manager = PluginManager.get(aj.context)
        ajentiPlugins = json.dumps(
                {manager[n]['info']['name']: manager[n]['info']['title'] for n in manager}
            )
        content = f'''
window.globalConstants = {{
    'urlPrefix': '{http_context.prefix}',
    'ajentiPlugins': {ajentiPlugins},
    'initialConfigContent': {json.dumps(aj.config.get_non_sensitive_data())},
    'ajentiPlatform': '{aj.platform_unmapped}',
    'ajentiPlatformUnmapped': '{aj.platform}',
    'ajentiVersion': '{aj.version}',
    'ajentiBootstrapColor': '{aj.config.data.get('color', None)}',
    'ajentiDevMode': '{aj.dev}',
}};
        '''

        http_context.add_header('Content-Type', 'application/javascript; charset=utf-8')
        http_context.respond_ok()

        return http_context.gzip(content=content.encode('utf-8'))

    @get('/resources/plugins.json')
    @endpoint(page=True, auth=False)
    def get_plugins(self, http_context):
        manager = PluginManager.get(aj.context)
        content = '['
        separator = ''
        for plugin_name in manager:
            if plugin_name == 'core':
                continue
            if '..' in plugin_name:
                return http_context.respond_not_found()


            plugin_info = manager[plugin_name]['info']
            frontend_settings = plugin_info['frontend-settings']

            widgetComponents = []
            if "widget-components" in frontend_settings:
                widgetComponents = frontend_settings['widget-components']

            remote_entry = frontend_settings['remote-entry'] if not frontend_settings['remote-entry'] == '' \
                else f'resources/{plugin_name}/frontend/dist/remoteEntry.js'

            content += f'''{separator}{{
    "remoteEntry": "{remote_entry}",
    "remoteName": "{frontend_settings['remote-name']}",
    "exposedModule": "{frontend_settings['exposed-module']}",
    "widgetComponents": {widgetComponents},
    "displayName": "{frontend_settings['display-name']}",
    "routePath": "{frontend_settings['route-path']}",
    "ngModuleName": "{frontend_settings['ng-module-name']}",
    "pluginName": "{plugin_info['name']}"
}}'''

            separator = ','

        content += ']'

        http_context.add_header('Content-Type', 'application/json; charset=utf-8')
        http_context.respond_ok()

        return http_context.gzip(content=content.encode('utf-8'))
