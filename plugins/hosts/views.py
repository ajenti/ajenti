from jadi import component
import subprocess
import os

from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError
from reconfigure.configs import HostsConfig
from reconfigure.items.hosts import AliasData, HostData


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/hosts')
    @endpoint(api=True)
    def handle_api_hosts(self, http_context):

        if http_context.method == 'GET':
            self.hosts_config = HostsConfig(path='/etc/hosts')
            self.hosts_config.load()
            return self.hosts_config.tree.to_dict()

        if http_context.method == 'POST':
            config = http_context.json_body()['config']
            new_hosts = HostsConfig(content='')
            new_hosts.load()

            for host in config:
                new_host = HostData()
                for property, value in host.items():
                    if property == 'aliases':
                        for alias in value:
                            if alias['name'] != '':
                                new_alias = AliasData()
                                new_alias.name = alias['name']
                                new_host.aliases.append(new_alias)
                    else:
                        setattr(new_host, property, value)
                new_hosts.tree.hosts.append(new_host)

            data = new_hosts.save()[None]

            # Always make a backup
            os.rename('/etc/hosts', '/etc/hosts.bak')

            try:
                with open('/etc/hosts', 'w') as f:
                    f.write(data)
                return True
            except Exception as e:
                raise EndpointError(e)



