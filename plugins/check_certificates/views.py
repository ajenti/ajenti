"""
Module to check if some certificates are still valid or not.
"""

from jadi import component

from aj.api.http import url, HttpPlugin
# from aj.auth import authorize
from aj.api.endpoint import endpoint
from .api import checkOnDom
import simplejson as json

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/check_cert/test')
    @endpoint(api=True)
    def handle_api_check_cert(self, http_context):
        """
        Connector between js and api to check the certification from one domain.
        The url given in post method is in the form www.domain.com:999.
        All urls are stored in the user config.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All details from a certificate
        :rtype: json
        """

        if http_context.method == 'POST':
            url = http_context.json_body()['url']
            return json.loads(json.dumps(checkOnDom(*url.split(':'))))

