import os
import re
import time
import subprocess

import ajenti
from ajenti.api import *
from ajenti.api.http import *
from ajenti.plugins import manager


@plugin
class ContentServer (HttpPlugin):
    last_query = 0

    @url('/ajenti:static/resources.(?P<type>.+)')
    def handle_resources(self, context, type):
        if ajenti.debug:
            if time.time() - self.last_query > 5:
                try:
                    print subprocess.check_output('./compile_resources.py nocompress', shell=True)
                except:
                    pass
                ContentCompressor.get().compress()
            self.last_query = time.time()
        content = ContentCompressor.get().compressed[type]
        types = {
            'css': 'text/css',
            'js': 'application/javascript',
        }
        context.add_header('Content-Type', types[type])
        return context.gzip(content)

    @url('/ajenti:static/(?P<plugin>\w+)/(?P<path>.+)')
    def handle_static(self, context, plugin, path):
        plugin_path = manager.resolve_path(plugin)
        if plugin_path is None:
            context.respond_not_found()
            return 'Not Found'
        path = os.path.join(plugin_path, 'content/static', path)
        return context.file(path)


@plugin
class ContentCompressor (object):
    def __init__(self):
        self.files = {}
        self.compressed = {}
        self.compressors = {
            'js': self.process_js,
            'css': self.process_css
        }
        self.patterns = {
            'js': r'.+\.[cm]\.js$',
            'css': r'.+\.[cm]\.css$'
        }
        self.scan()
        self.compress()

    def scan(self):
        for plugin in manager.get_order():
            pfiles = {}
            path = os.path.join(manager.resolve_path(plugin), 'content')
            if not os.path.exists(path):
                continue
            for (dp, dn, fn) in os.walk(path):
                for name in fn:
                    for key in self.patterns:
                        if re.match(self.patterns[key], name):
                            pfiles.setdefault(key, []).append(os.path.join(dp, name))
            for key in self.patterns:
                self.files.setdefault(key, []).extend(sorted(pfiles.setdefault(key, [])))

    def compress(self):
        for key in self.patterns:
            self.compressed[key] = self.compressors[key](self.files.setdefault(key, []))

    def process_js(self, files):
        return '\n'.join([open(x).read() for x in files])

    def process_css(self, files):
        return '\n'.join([open(x).read() for x in files])
