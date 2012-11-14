import json
import gevent
from base64 import b64encode
import zlib
import traceback

from ajenti.api import *
from ajenti.api.http import *
from ajenti.middleware import AuthenticationMiddleware
from ajenti.users import PermissionProvider, UserManager, SecurityError
from ajenti.ui import *
from ajenti.util import make_report

from api import SectionPlugin


@plugin
class MainServer (BasePlugin, HttpPlugin):
    @url('/')
    def handle_index(self, context):
        context.add_header('Content-Type', 'text/html')
        if context.session.identity is None:
            context.respond_ok()
            return self.open_content('static/auth.html').read()
        context.respond_ok()
        return self.open_content('static/index.html').read()

    @url('/auth')
    def handle_auth(self, context):
        username = context.query.getvalue('username', '')
        password = context.query.getvalue('password', '')
        if not AuthenticationMiddleware.get().try_login(context, username, password):
            gevent.sleep(3)
        return context.redirect('/')

    @url('/logout')
    def handle_logout(self, context):
        AuthenticationMiddleware.get().logout(context)
        context.session.destroy()
        return context.redirect('/')


@plugin
class MainSocket (SocketPlugin):
    name = '/stream'

    def on_connect(self):
        if not 'ui' in self.request.session.data:
            ui = UI()
            self.request.session.data['ui'] = ui
            ui.root = MainPage.new(ui)
            ui.root.username = self.request.session.identity
            sections_root = SectionsRoot.new(ui)
            ui.root.append(sections_root)
            ui._sections = sections_root.children
            ui._sections_root = sections_root

        self.ui = self.request.session.data['ui']
        self.send_ui()
        self.spawn(self.ui_watcher)
        self.context.notify = self.send_notify
        self.context.launch = self.launch
        self.context.endpoint = self

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
                if self.ui.has_updates():
                    self.ui.clear_updates()
                    self.send_ui()
        except SecurityError, e:
            self.send_security_error()
        except Exception, e:
            self.send_crash(e)

    def send_ui(self):
        data = json.dumps(self.ui.render())
        data = b64encode(zlib.compress(data)[2:-4])
        self.emit('ui', data)

    def send_update_request(self):
        self.emit('update-request')

    def send_security_error(self):
        self.emit('security-error', '')

    def send_url(self, url):
        self.emit('url', url)

    def send_crash(self, exc):
        data = {
            'message': str(exc),
            'traceback': traceback.format_exc(exc),
            'report': make_report()
        }
        data = json.dumps(data)
        self.emit('crash', data)

    def send_notify(self, text):
        self.emit('notify', text)

    def switch_tab(self, tab):
        self.ui._sections_root.on_switch(tab.uid)

    def launch(self, intent, **data):
        for section in self.ui._sections:
            for handler in section._intents:
                if handler == intent:
                    section._intents[handler](**data)
                    return

    def ui_watcher(self):
        while True:
            if self.ui.has_updates():
                self.send_update_request()
                gevent.sleep(0.5)
            gevent.sleep(0.2)


@plugin
class SectionPermissions (PermissionProvider):
    def get_name(self):
        return 'Section access'

    def get_permissions(self):
        return [
            ('section:%s' % x.__name__, x.__name__)
            for x in SectionPlugin.get_classes()
        ]


@p('username')
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
            try:
                UserManager.get().require_permission('section:%s' % cls.__name__)
                cat = cls.new(self.ui)
                self.append(cat)
            except SecurityError:
                pass
        self.children = sorted(self.children, key=lambda x: (self.category_order[x.category], x.order, x.title))
        if len(self.children) > 0:
            self.on_switch(self.children[0].uid)
        self.on('switch', self.on_switch)

    def on_switch(self, uid):
        for child in self.children:
            child.active = child.uid == uid
            if child.active:
                child.on_page_load()
            child.visible = child.active
