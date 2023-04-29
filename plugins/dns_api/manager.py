from aj.plugins.dns_api.api import ApiDnsManager
import aj

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

    def update_record(self, record):
        return self.api.update_record(self.fqdn, record)

    def delete_record(self, name):
        return self.api.delete_record(self.fqdn, name)


class DomainManager:

    def __init__(self, context):
        self.context = context
        # gandi is currently the only provider
        provider_id = aj.config.data.get('dns_api', {}).get('provider', 'gandi')

        for provider in ApiDnsManager.all(self.context):
            if provider.id == provider_id:
                self.api_provider = provider
                break
        self.domains = {}

    def load(self):
        self.get_domains()

    def get_domains(self):
        for domain in self.api_provider.get_domains():
            self.domains[domain] = Domain(domain, self)
