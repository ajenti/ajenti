from PIL import Image, ImageDraw
import StringIO
import json
import gzip
from base64 import b64decode, b64encode

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

        self.terminals = {0: Terminal()}
        print self.context.session.__dict__
        self.context.session.terminals = self.terminals
        self.refresh()

    def refresh(self):
        list = self.find('list')
        list.empty()
        for k in sorted(self.terminals.keys()):
            thumb = TerminalThumbnail(self.ui)
            thumb.tid = k
            list.append(thumb)


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

    def on_connect(self):
        pass

    def on_message(self, message):
        print message
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

"""
class TerminalPlugin(CategoryPlugin, URLHandler):
    text = 'Terminal'
    icon = '/dl/terminal/icon.png'
    folder = 'tools'

    def on_session_start(self):
        self._terminals = {}
        self._tid = 1
        self._terminals[0] = Terminal()
        
    def get_ui(self):
        ui = self.app.inflate('terminal:main')
        for id in self._terminals:
            ui.append('main', UI.TerminalThumbnail(
                id=id
            ))
        return ui

    @event('button/click')
    def onclick(self, event, params, vars=None):
        if params[0] == 'add':
            self._terminals[self._tid] = Terminal()
            self._tid += 1

    @event('term/kill')
    def onkill(self, event, params, vars=None):
        id = int(params[0])
        self._terminals[id].kill()
        del self._terminals[id]
    
    @url('^/terminal/.*$')
    def get(self, req, start_response):
        params = req['PATH_INFO'].split('/')[1:] + ['']
        id = int(params[1])

        if self._terminals[id].dead():
            self._terminals[id].start(self.app.get_config(self).shell)

        if params[2] in ['history', 'get']:
            if params[2] == 'history':
                data = self._terminals[id]._proc.history()
            else:
                data = self._terminals[id]._proc.read()
            sio = StringIO.StringIO()
            gz = gzip.GzipFile(fileobj=sio, mode='w')
            gz.write(json.dumps(data))
            gz.close()
            return b64encode(sio.getvalue())

        if params[2] == 'post':
            data = params[3]
            self._terminals[id].write(b64decode(data))
            return ''

        if params[2] == 'kill':
            self._terminals[id].restart()

        page = self.app.inflate('terminal:page')
        page.find('title').text = shell('echo `whoami`@`hostname`')
        page.append('main', UI.JS(
            code='termInit(\'%i\');'%id
        ))
        return page.render()


    @url('^/terminal-thumb/.*$')
    def get_thumb(self, req, start_response):
        params = req['PATH_INFO'].split('/')[1:]
        id = int(params[1])

        if self._terminals[id].dead():
            self._terminals[id].start(self.app.get_config(self).shell)

        img = Image.new("RGB", (TERM_W, TERM_H*2+20))
        draw = ImageDraw.Draw(img)
        draw.rectangle([0,0,TERM_W,TERM_H], fill=(0,0,0))

        colors = ['black', 'darkgrey', 'darkred', 'red', 'darkgreen',
                  'green', 'brown', 'yellow', 'darkblue', 'blue',
                  'darkmagenta', 'magenta', 'darkcyan', 'cyan',
                  'lightgrey', 'white'] 

        for y in range(0,TERM_H):
            for x in range(0,TERM_W):
                fc = self._terminals[id]._proc.term[y][x][1]
                if fc == 'default': fc = 'lightgray'
                fc = ImageDraw.ImageColor.getcolor(fc, 'RGB')
                bc = self._terminals[id]._proc.term[y][x][2]
                if bc == 'default': bc = 'black'
                bc = ImageDraw.ImageColor.getcolor(bc, 'RGB')
                ch = self._terminals[id]._proc.term[y][x][0]
                draw.point((x,10+y*2+1),fill=(fc if ord(ch) > 32 else bc))
                draw.point((x,10+y*2),fill=bc)

        sio = StringIO.StringIO()
        img.save(sio, 'PNG')
        start_response('200 OK', [('Content-type', 'image/png')])
        return sio.getvalue()

"""