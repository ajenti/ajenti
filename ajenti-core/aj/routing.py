import logging
import cgi
import traceback
from jadi import service

from aj.api.http import BaseHttpHandler, HttpPlugin


class InvalidRouteHandler(BaseHttpHandler):
    def __init__(self, context):
        pass

    def handle(self, http_context):
        logging.warn('URL not found: %s', http_context.path)
        http_context.respond_not_found()
        return 'URL not found'


@service
class CentralDispatcher(BaseHttpHandler):
    def __init__(self, context):
        self.context = context
        self.invalid = InvalidRouteHandler(context)

    def handle(self, context):
        """
        Dispatch the request to every HttpPlugin
        """

        for instance in HttpPlugin.all(self.context):
            try:
                output = instance.handle(context)
            # pylint: disable=W0703
            except Exception as e:
                return [self.respond_error(context, e)]
            if output is not None:
                return output
        return context.fallthrough(self.invalid)

    def respond_error(self, context, exception):
        context.respond_server_error()
        stack = traceback.format_exc()
        traceback.print_exc()
        return """
        <html>
            <body>

                <style>
                    body {
                        font-family: sans-serif;
                        color: #888;
                        text-align: center;
                    }

                    body pre {
                        width: 600px;
                        text-align: left;
                        margin: auto;
                        font-family: monospace;
                    }
                </style>

                <img src="/aj:static/main/error.jpeg" />
                <br/>
                <p>
                    Server error
                </p>
                <pre>
%s
                </pre>
            </body>
        </html>
        """ % cgi.escape(stack)
