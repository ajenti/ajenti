from base64 import b64encode
import catcher
import gevent
import gevent.coros
import json
import logging
import requests
import traceback
import zlib

import ajenti
from ajenti.api import *
from ajenti.api.http import *
from ajenti.api.sensors import Sensor
from ajenti.licensing import Licensing
from ajenti.middleware import AuthenticationMiddleware
from ajenti.plugins import manager
from ajenti.profiler import *
from ajenti.users import PermissionProvider, UserManager, SecurityError
from ajenti.ui import *
from ajenti.util import make_report
import ajenti.feedback

from api import SectionPlugin


@plugin
class MainServer (BasePlugin, HttpPlugin):
    @url('/')
    def handle_index(self, context):
        context.add_header('Content-Type', 'text/html')
        if context.session.identity is None:
            context.respond_ok()
            html = self.open_content('static/auth.html').read()
            return html % {
                'license': json.dumps(Licensing.get().get_license_status()),
                'error': json.dumps(context.session.data.pop('login-error', None)),
            }
        context.respond_ok()
        return self.open_content('static/index.html').read()

    @url('/ajenti:auth')
    def handle_auth(self, context):
        username = context.query.getvalue('username', '')
        password = context.query.getvalue('password', '')
        if not AuthenticationMiddleware.get().try_login(
            context, username, password, env=context.env,
        ):
            context.session.data['login-error'] = _('Invalid login or password')
            gevent.sleep(3)
        return context.redirect('/')

    @url('/ajenti:auth-persona')
    def handle_persona_auth(self, context):
        assertion = context.query.getvalue('assertion', None)
        audience = context.query.getvalue('audience', None)
        if not assertion:
            return self.context.respond_forbidden()

        data = {
            'assertion': assertion,
            'audience': audience,
        }

        resp = requests.post('https://verifier.login.persona.org/verify', data=data, verify=True)

        if resp.ok:
            verification_data = json.loads(resp.content)
            if verification_data['status'] == 'okay':
                context.respond_ok()
                email = verification_data['email']
                for user in ajenti.config.tree.users.values():
                    if user.email == email:
                        AuthenticationMiddleware.get().login(context, user.name)
                        break
                else:
                    context.session.data['login-error'] = _('Email "%s" is not associated with any user') % email
                return ''
        context.session.data['login-error'] = _('Login failed')
        return context.respond_not_found()

    @url('/ajenti:logout')
    def handle_logout(self, context):
        AuthenticationMiddleware.get().logout(context)
        context.session.destroy()
        return context.redirect('/')


@plugin
class MainSocket (SocketPlugin):
    name = '/stream'
    ui = None

    def on_connect(self):
        self.compression = 'zlib'
        self.__updater_lock = gevent.coros.RLock()

        # Inject into session
        self.request.session.endpoint = self

        # Inject the context methods
        self.context.notify = self.send_notify
        self.context.launch = self.launch
        self.context.endpoint = self

        if not 'ui' in self.request.session.data:
            # This is a newly created session
            ui = UI.new()

            self.request.session.data['ui'] = ui
            ui.root = MainPage.new(ui)
            ui.root.username = self.request.session.identity
            sections_root = SectionsRoot.new(ui)

            for e in sections_root.startup_crashes:
                self.send_crash(e)

            ui.root.append(sections_root)
            ui._sections = sections_root.children
            ui._sections_root = sections_root

        self.ui = self.request.session.data['ui']
        self.send_init()
        self.send_ui()
        self.spawn(self.ui_watcher)

    def on_message(self, message):
        if not self.ui:
            return
        self.spawn(self.handle_message, message)

    def handle_message(self, message):
        try:
            with self.__updater_lock:
                if message['type'] == 'ui_update':
                    # UI updates arrived
                    profile_start('Total')
                    # handle content updates first, before events affect UI
                    for update in message['content']:
                        if update['type'] == 'update':
                            # Property change
                            profile_start('Handling updates')
                            els = self.ui.root.nearest(
                                lambda x: x.uid == update['uid'],
                                exclude=lambda x: x.parent and not x.parent.visible,
                                descend=False,
                            )
                            if len(els) == 0:
                                continue
                            el = els[0]
                            for k, v in update['properties'].iteritems():
                                setattr(el, k, v)
                            profile_end('Handling updates')
                    for update in message['content']:
                        if update['type'] == 'event':
                            # Element event emitted
                            profile_start('Handling event')
                            self.ui.dispatch_event(update['uid'], update['event'], update['params'])
                            profile_end('Handling event')
                    if self.ui.has_updates():
                        # If any updates happened due to event handlers, send these immediately
                        self.ui.clear_updates()
                        self.send_ui()
                    else:
                        # Otherwise just ACK
                        self.send_ack()
                    profile_end('Total')
                    if ajenti.debug:
                        self.send_debug()
        except SecurityError as e:
            self.send_security_error()
        except Exception as e:
            catcher.backup(e)
            traceback.print_exc()
            e.traceback = traceback.format_exc(e)
            self.send_crash(e)

    def send_init(self):
        data = {
            'version': ajenti.version,
            'platform': ajenti.platform,
            'hostname': Sensor.find('hostname').value(),
            'session': self.context.session.id,
            'feedback': ajenti.config.tree.enable_feedback,
            'edition': ajenti.edition,
            'compression': self.compression,
        }
        self.emit('init', json.dumps(data))

    def send_ui(self):
        profile_start('Rendering')
        data = json.dumps(self.ui.render())
        profile_end('Rendering')
        if self.compression == 'zlib':
            data = b64encode(zlib.compress(data, 4)[2:-4])
        if self.compression == 'lzw':
            data = b64encode(self.__compress_lzw(data))
        self.emit('ui', data)

    def __compress_lzw(self, data):
        dict = {}
        out = []
        phrase = data[0]
        code = 256
        for i in range(1, len(data)):
            currChar = data[i]
            if dict.get(phrase + currChar, None):
                phrase += currChar
            else:
                out.append(dict[phrase] if (len(phrase) > 1) else ord(phrase[0]))
                dict[phrase + currChar] = code
                code += 1
                phrase = currChar
        out.append(dict[phrase] if (len(phrase) > 1) else ord(phrase[0]))
        res = ''
        for code in out:
            if code >= 256:
                res += chr(0)
                res += chr(code / 256)
            res += chr(code % 256)
        return res

    def send_ack(self):
        self.emit('ack')

    def send_progress(self, msg=''):
        self.emit('progress-message', msg)
        gevent.sleep(0)

    def send_update_request(self):
        self.emit('update-request')

    def send_security_error(self):
        self.emit('security-error', '')

    def send_open_tab(self, url, title='new tab'):
        self.emit('openTab', json.dumps({'url': url, 'title': title}))

    def send_close_tab(self, url):
        self.emit('closeTab', json.dumps({'url': url}))

    def send_debug(self):
        profiles = get_profiles()
        logging.debug(repr(profiles))
        data = {
            'profiles': profiles
        }
        self.emit('debug', json.dumps(data))

    def send_crash(self, exc):
        if not hasattr(exc, 'traceback'):
            traceback.print_exc()
            exc.traceback = traceback.format_exc(exc)
        data = {
            'message': str(exc),
            'traceback': exc.traceback,
            'report': make_report(exc)
        }
        data = json.dumps(data)
        self.emit('crash', data)

    def send_notify(self, type, text):
        self.emit('notify', json.dumps({'type': type, 'text': text}))

    def switch_tab(self, tab):
        self.ui._sections_root.on_switch(tab.uid)

    def launch(self, intent, **data):
        for section in self.ui._sections:
            for handler in section._intents:
                if handler == intent:
                    section._intents[handler](**data)
                    return

    def get_section(self, cls):
        for section in self.ui._sections:
            if section.__class__ == cls:
                return section

    def ui_watcher(self):
        # Sends UI updates periodically
        while True:
            if self.__updater_lock:
                if self.ui.has_updates():
                    self.send_update_request()
                    gevent.sleep(0.5)
            gevent.sleep(0.2)


@plugin
class SectionPermissions (PermissionProvider):
    def get_name(self):
        return _('Section access')

    def get_permissions(self):
        # Generate permission set on-the-fly
        return sorted([
            ('section:%s' % x.__class__.__name__, (_(x.category) or 'Ajenti') + ' | ' + _(x.title))
            for x in SectionPlugin.get_instances()
            if not hasattr(x, 'permissionless') and not hasattr(x, 'uses_access_permission_of')
        ], key=lambda x: x[1])


@p('username')
@plugin
class MainPage (UIElement, BasePlugin):
    typeid = 'main:page'


@p('name')
@plugin
class SectionsCategory (UIElement):
    typeid = 'main:sections_category'


@p('is_empty', type=bool)
@plugin
class SectionsRoot (UIElement):
    typeid = 'main:sections_root'
    category_order = {
        '': 0,
        'System': 50,
        'Web': 60,
        'Tools': 70,
        'Software': 80,
        'Other': 99
    }

    def init(self):
        self.categories = {}
        self.startup_crashes = []

        profile_start('Starting plugins')

        self.is_empty = True
        for cls in SectionPlugin.get_classes():
            try:
                if not hasattr(cls, 'permissionless'):
                    permission_target = cls
                    if hasattr(cls, 'uses_access_permission_of'):
                        permission_target = cls.uses_access_permission_of
                    UserManager.get().require_permission(self.context, 'section:%s' % permission_target.__name__)

                try:
                    profile_start('Starting %s' % cls.__name__)
                    cat = cls.new(self.ui)
                    cat.clsname = cls.classname
                    profile_end()
                    self.append(cat)
                    self.is_empty = False
                except SecurityError:
                    pass
                except Exception as e:
                    catcher.backup(e)
                    traceback.print_exc()
                    e.traceback = traceback.format_exc(e)
                    self.startup_crashes.append(e)
            except SecurityError:
                pass

        profile_end()

        def category_order(x):
            order = 98
            if x.category in self.category_order:
                order = self.category_order[x.category]
            return (order, x.order, x.title)

        self.children = sorted(self.children, key=category_order)
        if len(self.children) > 0:
            self.on_switch(self.children[0].uid)

    def on_switch(self, uid):
        for child in self.children:
            child.active = child.uid == uid
            child.visible = child.active
            if child.active:
                if child._first_page_load:
                    child.broadcast('on_first_page_load')
                    child._first_page_load = False
                child.broadcast('on_page_load')
        self.invalidate()
