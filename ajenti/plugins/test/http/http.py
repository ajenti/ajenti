from ajenti.api import plugin, BasePlugin
from ajenti.api.http import HttpPlugin, url


@plugin
class HttpDemo (BasePlugin, HttpPlugin):
    @url('/ajenti:demo/notify')
    def get_page(self, context):
        if context.session.identity is None:
            context.respond_redirect('/')
        self.context.notify('info', context.query.getvalue('text', ''))
        context.respond_ok()
        return ''

    @url('/ajenti:demo/respond/(?P<what>.+)')
    def get_response(self, context, what=None):
        if what == 'ok':
            context.respond_ok()
            return 'Hello!'
        if what == 'redirect':
            return context.respond_redirect('/')
        if what == 'server_error':
            return context.respond_server_error()
        if what == 'forbidden':
            return context.respond_forbidden()
        if what == 'not_found':
            return context.respond_not_found()
        if what == 'file':
            return context.file('/etc/issue')
        if what == 'error':
            raise Exception('error!')