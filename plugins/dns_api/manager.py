from aj.plugins.dns_api.api import ApiDnsManager

class Domain:

    def __init__(self, fqdn, manager):
        self.fqdn = fqdn
        self.mgr = manager
        self.api = manager.api_provider
        self.records = []

    def get_records(self):
        self.api.get_records(self)

    def add_record(self, record):
        return self.api.add_record(self.fqdn, record)


class DomainManager:

    def __init__(self, context):
        self.context = context
        for provider in ApiDnsManager.all(self.context):
            # TODO : gandi is the only one, need to prepare a config entry
            if provider.id == 'gandi':
                self.api_provider = provider
                break
        self.domains = {}

    def load(self):
        self.get_domains()

    def get_domains(self):
        for domain in self.api_provider.get_domains():
            self.domains[domain] = Domain(domain, self)
