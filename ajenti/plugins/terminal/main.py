from base64 import b64decode, b64encode
import gzip
import json
from PIL import Image, ImageDraw
import StringIO

from ajenti.api import *
from ajenti.api.http import HttpPlugin, url, SocketPlugin
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import UIElement, p

from terminal import Terminal


@plugin
class Terminals (SectionPlugin):
    def init(self):
        self.title = 'Terminal'
        self.category = 'Tools'

        self.append(self.ui.inflate('terminal:main'))
        self.find('new-button').on('click', self.on_new)

        self.terminals = {}
        self.context.session.terminals = self.terminals
        self.refresh()

    def refresh(self):
        list = self.find('list')
        list.empty()
        for k in sorted(self.terminals.keys()):
            thumb = TerminalThumbnail(self.ui)
            thumb.tid = k
            thumb.on('close', self.on_close, k)
            list.append(thumb)

    def on_new(self):
        if self.terminals:
            key = sorted(self.terminals.keys())[-1] + 1
        else:
            key = 0
        self.terminals[key] = Terminal()
        self.refresh()
        self.publish()

    def on_close(self, k):
        self.terminals[k].kill()
        self.terminals.pop(k)
        self.refresh()
        self.publish()


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
            self.id = message['tid']
            self.terminal = self.context.session.terminals[int(message['tid'])]
            self.send_data(self.terminal.protocol.history())
            self.spawn(self.worker)
        if message['type'] == 'key':
            ch = b64decode(message['key'])
            self.terminal.write(ch)

    def worker(self):
        while True:
            self.send_data(self.terminal.protocol.read())

    def send_data(self, data):
        sio = StringIO.StringIO()
        gz = gzip.GzipFile(fileobj=sio, mode='w')
        gz.write(json.dumps(data))
        gz.close()
        self.emit('set', b64encode(sio.getvalue()))
