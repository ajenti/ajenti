import logging
import os
import cgi
import traceback
import base64
from jadi import service

from aj.api.http import BaseHttpHandler, HttpPlugin

class DeniedRouteHandler(BaseHttpHandler):
    """If client authentication is forced, and the client certificate is not valid."""

    def __init__(self, context):
        pass

    def handle(self, http_context):
        logging.warning('Invalid client certificate : %s', http_context.env['SSL_CLIENT_DIGEST'])
        http_context.respond_unauthenticated()

        return ["""
        <!DOCTYPE html>
        <html>
            <body>

                <style>
                    body {
                        font-family: sans-serif;
                        color: #888;
                        text-align: center;
                    }
                </style>
                <p>
                    401 - Unauthenticated
                </p>
            </body>
        </html>
        """]

class InvalidRouteHandler(BaseHttpHandler):
    def __init__(self, context):
        pass

    def handle(self, http_context):
        logging.warning('URL not found: %s', http_context.path)
        http_context.respond_not_found()
        
        with open(os.path.dirname(__file__)+'/static/images/error.jpeg', "rb") as error_image:
            error_encoded = base64.b64encode(error_image.read()).decode()
            
        return ["""
        <!DOCTYPE html>
        <html>
            <body>

                <style>
                    body {
                        font-family: sans-serif;
                        color: #888;
                        text-align: center;
                    }
                </style>
                
                <img src="data:image/png;base64, %s" alt="Error image" />
                <br/>
                <p>
                    404 - URL not found
                </p>
                <p>
                    <a href="/">Return to ajenti panel</a> 
                </p>
            </body>
        </html>
        """ % error_encoded]

@service
class CentralDispatcher(BaseHttpHandler):
    def __init__(self, context):
        self.context = context
        self.invalid = InvalidRouteHandler(context)
        self.denied = DeniedRouteHandler(context)

    def handle(self, http_context):
        """
        Dispatch the request to every HttpPlugin
        """

        if http_context.env['SSL_CLIENT_AUTH_FORCE'] and not http_context.env['SSL_CLIENT_VALID']:
            return http_context.fallthrough(self.denied)

        for instance in HttpPlugin.all(self.context):
            try:
                output = instance.handle(http_context)
            # pylint: disable=W0703
            except Exception as e:
                return [self.respond_error(http_context, e)]
            if output is not None:
                return output
        return http_context.fallthrough(self.invalid)

    def respond_error(self, http_context, exception):
        http_context.respond_server_error()
        stack = traceback.format_exc()
        traceback.print_exc()
        
        with open(os.path.dirname(__file__)+'/static/images/error.jpeg', "rb") as error_image:
            error_encoded = base64.b64encode(error_image.read()).decode()
        
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

                <img src="data:image/png;base64, %s" alt="Error image" />
                <br/>
                <p>
                    Server error
                </p>
                <pre>%s</pre>
            </body>
        </html>
        """ % (error_encoded, cgi.escape(stack))
