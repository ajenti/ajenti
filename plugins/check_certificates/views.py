from jadi import component

from aj.api.http import url, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint, EndpointError
from .api import checkOnDom
import simplejson as json

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/check_cert/test')
    @endpoint(api=True)
    def handle_api_check_cert(self, http_context):
        if http_context.method == 'POST':
            url = http_context.json_body()['url']
            return json.loads(json.dumps(checkOnDom(*url.split(':'))))
            
