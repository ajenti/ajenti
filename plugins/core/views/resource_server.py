import json
import os
from jadi import component

import aj
from aj.api.http import url, HttpPlugin
from aj.plugins import PluginManager

from aj.api.endpoint import endpoint


@component(HttpPlugin)
class ResourcesHandler(HttpPlugin):
    def __init__(self, http_context):
        self.cache = {}
        self.use_cache = not aj.debug
        self.mgr = PluginManager.get(aj.context)

    @url(r'/resources/all\.(?P<type>.+)')
    @endpoint(page=True, auth=False)
    def handle_build(self, http_context, type=None):
        if self.use_cache and type in self.cache:
            content = self.cache[type]
        else:
            content = ''
            if type in ['js', 'css']:
                for plugin in self.mgr:
                    path = self.mgr.get_content_path(plugin, 'resources/build/all.%s' % type)
                    if os.path.exists(path):
                        content += open(path).read()
            if type == 'init.js':
                ng_modules = []
                for plugin in self.mgr:
                    for resource in self.mgr[plugin]['info']['resources']:
                        if resource.startswith('ng:'):
                            ng_modules.append(resource.split(':')[-1])
                content = '''
                    window.__ngModules = %s;
                ''' % json.dumps(ng_modules)
            if type == 'locale.js':
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
                        if resource.endswith('.html'):
                            path = self.mgr.get_content_path(plugin, resource)
                            if os.path.exists(path):
                                template = open(path).read()
                                content += '''
                                      $templateCache.put("%s", %s);
                                ''' % (
                                    '%s/%s:%s' % (http_context.prefix, plugin, resource),
                                    json.dumps(template)
                                )
                content += '''
                    }]);
                '''

            self.cache[type] = content

        http_context.add_header('Content-Type', {
            'css': 'text/css',
            'js': 'application/javascript; charset=utf-8',
            'init.js': 'application/javascript; charset=utf-8',
            'locale.js': 'application/javascript; charset=utf-8',
            'partials.js': 'application/javascript; charset=utf-8',
        }[type])
        http_context.respond_ok()
        return http_context.gzip(content=content.encode('utf-8'))

    @url(r'/resources/(?P<plugin>\w+)/(?P<path>.+)')
    @endpoint(page=True, auth=False)
    def handle_file(self, http_context, plugin=None, path=None):
        if '..' in path:
            return http_context.respond_not_found()
        return http_context.file(PluginManager.get(aj.context).get_content_path(plugin, path))
