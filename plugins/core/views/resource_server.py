import json
import os
import hashlib
import time
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

    @get(r'/resources/all\.(?P<group>.+)')
    @endpoint(page=True, auth=False)
    def handle_build(self, http_context, group=None):
        """
        Deliver all extern resources for the current page.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param group: File extension/type, e.g. css, js ...
        :type group: string
        :return: Compressed content with gzip
        :rtype: gzip
        """


        sid = http_context.env.get('REMOTE_ADDR', '')
        sid += http_context.env.get('HTTP_USER_AGENT', '')
        sid += http_context.env.get('HTTP_HOST', '')
        cache_id = hashlib.sha256(sid.encode('utf-8')).hexdigest()

        if cache_id not in self.cache:
            self.cache[cache_id] = {'timestamp': int(time.time())}

        if self.use_cache and group in self.cache[cache_id]:
            content = self.cache[cache_id][group]
            now = int(time.time())
            self.cache[cache_id]['timestamp'] = now

            # Delete cache older than 1h
            dead_cache_id = [cid  for cid, cache in self.cache.items() if now - cache['timestamp'] > 3600]
            for cid in dead_cache_id:
                del self.cache[cid]

        else:
            content = ''
            if group in ['js', 'css', 'vendor.js', 'vendor.css']:
                for plugin in self.mgr:
                    path = self.mgr.get_content_path(plugin, f'resources/build/all.{group}')
                    if os.path.exists(path):
                        with open(path, encoding="utf-8") as f:
                            file_content = f.read()
                        if group == 'js':
                            file_content = self.__wrap_js(path, file_content)
                        content += file_content
            if group == 'init.js':
                ng_modules = {}
                for plugin in self.mgr:
                    for resource in self.mgr[plugin]['info']['resources']:
                        if resource['path'].startswith('ng:'):
                            ng_modules.setdefault(plugin, []).append(resource['path'].split(':')[-1])
                content = f'''
                    window.__ngModules = {json.dumps(ng_modules)};
                '''
            if group == 'locale.js':
                lang = http_context.query.get('lang', None)
                if lang:
                    js_locale = {}
                    for plugin in self.mgr:
                        locale_dir = self.mgr.get_content_path(plugin, 'locale')
                        js_path = os.path.join(locale_dir, lang, 'LC_MESSAGES', 'app.js')
                        if os.path.exists(js_path):
                            with open(js_path, encoding='utf-8') as j:
                                js_locale.update(json.load(j))
                    content = json.dumps(js_locale)
                else:
                    content = ''
            if group == 'partials.js':
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
                                with open(path, encoding='utf-8') as t:
                                    template = t.read()
                                content += f'''
                                      $templateCache.put("{http_context.prefix}/{name}", {json.dumps(template)});
                                '''
                content += '''
                    }]);
                '''

            self.cache[cache_id][group] = content

        http_context.add_header('Content-Type', {
            'css': 'text/css',
            'js': 'application/javascript; charset=utf-8',
            'vendor.css': 'text/css',
            'vendor.js': 'application/javascript; charset=utf-8',
            'init.js': 'application/javascript; charset=utf-8',
            'locale.js': 'application/javascript; charset=utf-8',
            'partials.js': 'application/javascript; charset=utf-8',
        }[group])
        http_context.respond_ok()

        return http_context.gzip(content=content.encode('utf-8'))

    @get(r'/resources/(?P<plugin>\w+)/(?P<path>.+)')
    @endpoint(page=True, auth=False)
    def handle_file(self, http_context, plugin=None, path=None):
        """
        Connector to get a specific file from plugin.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param plugin: Plugin name
        :type plugin: string
        :param path: Path of the file
        :type path: string
        :return: Compressed content of the file
        :rtype: gzip
        """

        if '..' in path:
            return http_context.respond_not_found()
        return http_context.file(PluginManager.get(aj.context).get_content_path(plugin, path))
