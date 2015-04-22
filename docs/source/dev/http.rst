.. _dev-http:

Handling HTTP Requests
**********************

Example
=======

Basic HTTP API example can be browsed and downloaded at https://github.com/ajenti/demo-plugins/tree/master/demo_4_http

Plugins can provide their own HTTP endpoints by extending the :class:`aj.api.http.HttpPlugin` abstract class.

Example::

    import time
    from jadi import component

    from aj.api.http import url, HttpPlugin

    from aj.api.endpoint import endpoint, EndpointError, EndpointReturn


    @component(HttpPlugin)
    class Handler(HttpPlugin):
        def __init__(self, context):
            self.context = context

        @url(r'/api/demo4/calculate/(?P<operation>\w+)/(?P<a>\d+)/(?P<b>\d+)')
        @endpoint(api=True)
        def handle_api_calculate(self, http_context, operation=None, a=None, b=None):
            start_time = time.time()

            try:
                if operation == 'add':
                    result = int(a) + int(b)
                elif operation == 'divide':
                    result = int(a) / int(b)
                else:
                    raise EndpointReturn(404)
            except ZeroDivisionError:
                raise EndpointError('Division by zero')

            return {
                'value': result,
                'time': time.time() - start_time
            }


``@endpoint(api=True)`` mode provides automatic JSON encoding of the responses and error handling.

If you need lower-level access to the HTTP response, use ``@endpoint(page=True)``::

        @url(r'/api/test')
        @endpoint(page=True)
        def handle_api_calculate(self, http_context):
            http_context.add_header('Content-Type', '...')
            content = "Hello!"
            #return http_context.respond_not_found()
            #return http_context.respond_forbidden()
            #return http_context.file('/some/path')
            http_context.respond_ok()
            return content

See :class:`aj.http.HttpContext` for the available ``http_context`` methods.