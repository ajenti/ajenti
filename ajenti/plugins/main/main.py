import os
import json
import gevent

from ajenti.api import *
from ajenti.api.http import *
from ajenti.plugins import manager
from ajenti.ui import *
from ajenti.middleware import AuthenticationMiddleware

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
class MainSocket (BasePlugin, SocketPlugin):
    name = '/stream'

    def on_connect(self):
        if not 'ui' in self.socket.session.data:
            ui = UI()
            self.socket.session.data['ui'] = ui
            ui.root = MainPage(ui)
            ui.root.append(SectionsRoot(ui))

        self.ui = self.socket.session.data['ui']
        self.send_ui()
        self.spawn(self.ui_watcher)

    def on_message(self, message):
        if message['type'] == 'ui_update':
            for update in message['content']:
                if update['type'] == 'event':
                    self.ui.dispatch_event(update['uid'], update['event'], update['params'])
                if update['type'] == 'update':
                    el = self.ui.find_uid(update['uid'])
                    for k, v in update['properties'].iteritems():
                        el.properties[k].set(v)
                        el.properties[k].dirty = False

    def send_ui(self):
        data = json.dumps(self.ui.render())
        self.emit('ui', data)

    def ui_watcher(self):
        while True:
            updates = self.ui.get_updates()
            if len(updates) > 0:
                self.send_ui()
            gevent.sleep(0.2)


@plugin
class MainPage (UIElement):
    typeid = 'main:page'


@plugin
class SectionsRoot (UIElement):
    typeid = 'main:sections_root'

    def init(self):
        for cls in SectionPlugin.get_classes():
            cat = cls.new(self.ui)
            self.append(cat)
        self.children[0].active = True
        self.on('switch', self.on_switch)

    def on_switch(self, uid):
        for child in self.children:
            child.active = child.uid == uid
        self.publish()

