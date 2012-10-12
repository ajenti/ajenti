import json
import gevent
from base64 import b64encode
import StringIO
import gzip
import traceback

from ajenti.api import *
from ajenti.api.http import *
from ajenti.ui import *
from ajenti.middleware import AuthenticationMiddleware
from ajenti.util import make_report

from api import SectionPlugin


@plugin
class MainServer (BasePlugin, HttpPlugin):

    @url('/')
    def handle_index(self, context):
        if context.session.identity is None:
            context.respond_ok()
            return self.open_content('static/auth.html').read()
        context.add_header('Content-Type', 'text/html')
        context.respond_ok()
        return self.open_content('static/index.html').read()

    @url('/auth')
    def handle_auth(self, context):
        username = context.query.getvalue('username', '')
        password = context.query.getvalue('password', '')
        if not AuthenticationMiddleware.get().try_login(context, username, password):
            gevent.sleep(3)
        return context.redirect('/')


@plugin
class MainSocket (SocketPlugin):
    name = '/stream'

    def on_connect(self):
        if not 'ui' in self.socket.session.data:
            ui = UI()
            self.socket.session.data['ui'] = ui
            ui.root = MainPage.new(ui)
            root = SectionsRoot.new(ui)
            ui.root.append(root)

        self.ui = self.socket.session.data['ui']
        self.send_ui()
        self.spawn(self.ui_watcher)

    def on_message(self, message):
        try:
            if message['type'] == 'ui_update':
                for update in message['content']:
                    if update['type'] == 'event':
                        self.ui.dispatch_event(update['uid'], update['event'], update['params'])
                    if update['type'] == 'update':
                        el = self.ui.find_uid(update['uid'])
                        for k, v in update['properties'].iteritems():
                            el.properties[k].set(v)
                            el.properties[k].dirty = False
        except Exception, e:
            self.send_crash(e)

    def send_ui(self):
        data = json.dumps(self.ui.render())
        sio = StringIO.StringIO()
        gz = gzip.GzipFile(fileobj=sio, mode='w')
        gz.write(data)
        gz.close()
        data = b64encode(sio.getvalue())
        self.emit('ui', data)

    def send_crash(self, exc):
        data = {
            'message': str(exc),
            'traceback': traceback.format_exc(exc),
            'report': make_report()
        }
        data = json.dumps(data)
        self.emit('crash', data)

    def ui_watcher(self):
        while True:
            updates = self.ui.get_updates()
            if len(updates) > 0:
                self.send_ui()
            gevent.sleep(0.1)


@plugin
class MainPage (UIElement):
    typeid = 'main:page'


@p('name')
@plugin
class SectionsCategory (UIElement):
    typeid = 'main:sections_category'


@plugin
class SectionsRoot (UIElement):
    typeid = 'main:sections_root'
    category_order = {
        'Ajenti': 0,
        'System': 50,
        'Tools': 60,
        'Software': 80,
        'Other': 99
    }

    def init(self):
        self.categories = {}
        for cls in SectionPlugin.get_classes():
            cat = cls.new(self.ui)
            self.append(cat)
        self.children = sorted(self.children, key=lambda x: (self.category_order[x.category], x.order, x.title))
        self.children[0].active = True
        self.on('switch', self.on_switch)

    def on_switch(self, uid):
        for child in self.children:
            child.active = child.uid == uid
        self.publish()
