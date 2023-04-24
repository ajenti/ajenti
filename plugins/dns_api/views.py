from jadi import component
from dataclasses import asdict

from aj.api.http import get, put, post, HttpPlugin
from aj.auth import authorize
from aj.plugins.dns_api.record import Record
from aj.api.endpoint import endpoint, EndpointError
from aj.plugins.dns_api.manager import DomainManager


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context
        self.mgr = DomainManager(self.context)


    @get(r'/api/dns_api/domains')
    @endpoint(api=True)
    def handle_api_dns_list_domains(self, http_context):
        self.mgr.load()
        return list(self.mgr.domains.keys())

    @get(r'/api/dns_api/domain/(?P<fqdn>[\w\.]+)/records')
    @endpoint(api=True)
    def handle_api_dns_list_records(self, http_context, fqdn):
        self.mgr.domains[fqdn].get_records()
        return [asdict(r) for r in self.mgr.domains[fqdn].records]

    @post(r'/api/dns_api/domain/(?P<fqdn>[\w\.]+)/records/(?P<name>.*)')
    @endpoint(api=True)
    def handle_api_dns_put_record(self, http_context, fqdn, name):
        record = Record (
            name,
            http_context.json_body()['ttl'],
            http_context.json_body()['type'],
            [http_context.json_body()['values']]
        )
        return self.mgr.domains[fqdn].add_record(record)