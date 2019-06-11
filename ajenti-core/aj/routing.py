import logging
import os
import cgi
import traceback
import base64
from jadi import service

from aj.api.http import BaseHttpHandler, HttpPlugin


class InvalidRouteHandler(BaseHttpHandler):
    def __init__(self, context):
        pass

    def handle(self, http_context):
        logging.warn('URL not found: %s', http_context.path)
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
