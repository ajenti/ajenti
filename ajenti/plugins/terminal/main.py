from base64 import b64decode, b64encode
import zlib
import json
from PIL import Image, ImageDraw
import StringIO

from ajenti.api import *
from ajenti.api.http import HttpPlugin, url, SocketPlugin
from ajenti.plugins.main.api import SectionPlugin, intent
from ajenti.ui import UIElement, p, on

from terminal import Terminal


@plugin
class Terminals (SectionPlugin):
    def init(self):
        self.title = 'Terminal'
        self.icon = 'list-alt'
        self.category = 'Tools'

        self.append(self.ui.inflate('terminal:main'))

        self.terminals = {}
        self.context.session.terminals = self.terminals

    def on_page_load(self):
        self.refresh()

    @intent('terminals:refresh')
    def refresh(self):
        ulist = self.find('list')
        ulist.empty()
        for k, v in list(self.terminals.iteritems()):
            if v.autoclose and v.dead():
                self.terminals.pop(k)
        for k in sorted(self.terminals.keys()):
            thumb = TerminalThumbnail(self.ui)
            thumb.tid = k
            thumb.on('close', self.on_close, k)
            ulist.append(thumb)

    @intent('terminal')
    def launch(self, command=None):
        key = self.on_new(command, autoclose=True)
        self.context.endpoint.send_url('/terminal/%i' % key)

    @on('new-button', 'click')
    def on_new(self, command=None, **kwargs):
        if self.terminals:
            key = sorted(self.terminals.keys())[-1] + 1
        else:
            key = 0
        self.terminals[key] = Terminal(command, **kwargs)
        self.refresh()
        return key

    def on_close(self, k):
        self.terminals[k].kill()
        self.terminals.pop(k)
        self.refresh()


@plugin
class TerminalHttp (BasePlugin, HttpPlugin):
    @url('/terminal/(?P<id>\d+)')
    def get_page(self, context, id):
        if context.session.identity is None:
            context.respond_redirect('/')
        context.add_header('Content-Type', 'text/html')
        context.respond_ok()
        return self.open_content('static/index.html').read()

    @url('/terminal/(?P<id>\d+)/thumbnail')
    def get_thumbnail(self, context, id):
        terminal = context.session.terminals[int(id)]

        img = Image.new("RGB", (terminal.width, terminal.height * 2 + 20))
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, terminal.width, terminal.height], fill=(0, 0, 0))

        for y in range(0, terminal.height):
            for x in range(0, terminal.width):
                fc = terminal.screen[y][x][1]
                if fc == 'default':
                    fc = 'lightgray'
                fc = ImageDraw.ImageColor.getcolor(fc, 'RGB')
                bc = terminal.screen[y][x][2]
                if bc == 'default':
                    bc = 'black'
                bc = ImageDraw.ImageColor.getcolor(bc, 'RGB')
                ch = terminal.screen[y][x][0]
                draw.point((x, 10 + y * 2 + 1), fill=(fc if ord(ch) > 32 else bc))
                draw.point((x, 10 + y * 2), fill=bc)

        sio = StringIO.StringIO()
        img.save(sio, 'PNG')

        context.add_header('Content-type', 'image/png')
        context.respond_ok()
        return sio.getvalue()


@p('tid', default=0, type=int)
@plugin
class TerminalThumbnail (UIElement):
    typeid = 'terminal:thumbnail'


@plugin
class TerminalSocket (SocketPlugin):
    name = '/terminal'

    def on_message(self, message):
        if message['type'] == 'select':
            self.id = int(message['tid'])
            self.terminal = self.context.session.terminals[self.id]
            self.send_data(self.terminal.protocol.history())
            self.spawn(self.worker)
        if message['type'] == 'key':
            ch = b64decode(message['key'])
            self.terminal.write(ch)

    def worker(self):
        while True:
            self.send_data(self.terminal.protocol.read())
            if self.terminal.dead():
                del self.context.session.terminals[self.id]
                self.context.launch('terminals:refresh')
                return

    def send_data(self, data):
        self.emit('set', b64encode(zlib.compress(json.dumps(data))[2:-4]))
