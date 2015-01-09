from ajenti.util import LazyModule
Image = LazyModule('PIL.Image')
ImageDraw = LazyModule('PIL.ImageDraw')

import gevent
import StringIO

import ajenti
from ajenti.api import *
from ajenti.api.http import url, HttpPlugin, SocketEndpoint
from ajenti.plugins.core.api.endpoint import endpoint

from manager import TerminalManager


@component(HttpPlugin)
class Handler (HttpPlugin):
    def __init__(self, context):
        self.context = context
        self.mgr = TerminalManager.get(self.context)

    @url('/api/terminal/list')
    @endpoint(api=True)
    def handle_list(self, http_context):
        return self.mgr.list()

    @url('/api/terminal/create')
    @endpoint(api=True)
    def handle_create(self, http_context):
        return self.mgr.create()

    @url(r'/api/terminal/kill/(?P<id>.+)')
    @endpoint(api=True)
    def handle_kill(self, http_context, id=None):
        return self.mgr.kill(id)

    @url(r'/api/terminal/full/(?P<id>.+)')
    @endpoint(api=True)
    def handle_full(self, http_context, id=None):
        return self.mgr[id].format(full=True)


    colors = {
        'black': '#073642',
        'white': '#eee8d5',
        'green': '#859900',
        'yellow': '#b58900',
        'red': '#dc322f',
        'magenta': '#d33682',
        'violet': '#6c71c4',
        'blue': '#268bd2',
        'cyan': '#2aa198',
    }

    @url(r'/api/terminal/preview/(?P<id>.+)')
    @endpoint(page=True)
    def handle_preview(self, http_context, id):
        terminal = self.mgr[id]

        img = Image.new('RGB', (terminal.width, terminal.height * 2))
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, terminal.width, terminal.height], fill=ImageDraw.ImageColor.getcolor(self.colors['black'], 'RGB'))

        for y in range(0, terminal.height):
            for x in range(0, terminal.width):
                fc = terminal.screen.buffer[y][x][1]
                if fc == 'default':
                    fc = 'lightgray'
                if fc in self.colors:
                    fc = self.colors[fc]
                fc = ImageDraw.ImageColor.getcolor(fc, 'RGB')
                bc = terminal.screen.buffer[y][x][2]
                if bc == 'default':
                    bc = 'black'
                if bc in self.colors:
                    bc = self.colors[bc]
                bc = ImageDraw.ImageColor.getcolor(bc, 'RGB')
                ch = terminal.screen.buffer[y][x][0]
                draw.point((x, y * 2 + 1), fill=(fc if ord(ch) > 32 else bc))
                draw.point((x, y * 2), fill=bc)

        sio = StringIO.StringIO()
        img.save(sio, 'PNG')

        http_context.add_header('Content-Type', 'image/png')
        http_context.respond_ok()
        return sio.getvalue()


@component(SocketEndpoint)
class Socket (SocketEndpoint):
    plugin = 'terminal'

    def __init__(self, context):
        SocketEndpoint.__init__(self, context)
        self.mgr = TerminalManager.get(self.context)
        self.readers = {}

    def on_message(self, message, *args):
        if message['action'] == 'subscribe':
            id = message['id']
            if id in self.readers:
                self.readers[id].kill(block=False)
            self.readers[id] = gevent.spawn(self.reader, id)
            # todo: spawn in namespace
            #self.spawn(self.reader, terminal)
        if message['action'] == 'input':
            terminal = self.mgr[message['id']]
            terminal.feed(message['data'])
        if message['action'] == 'resize':
            terminal = self.mgr[message['id']]
            terminal.resize(message['width'], message['height'])

    def reader(self, id):
        terminal = self.mgr[id]
        q = terminal.output.register()
        while True:
            data = q.get()
            data['id'] = id
            self.send(data)


