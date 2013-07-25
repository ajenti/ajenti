.. _dev-http:

Handling HTTP Requests
**********************

Example
=======

This example illustrates various HTTP responses.
Try following URLs:

  * http://localhost:8000/ajenti:demo/notify?text=hello
  * http://localhost:8000/ajenti:demo/respond/redirect
  * http://localhost:8000/ajenti:demo/respond/server_error
  * http://localhost:8000/ajenti:demo/respond/ok
  * http://localhost:8000/ajenti:demo/respond/file

Code::

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

`Download this example </_static/dev/test_http.tar.gz>`_
