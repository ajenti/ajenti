from jadi import component
import subprocess

from aj.api.http import get, post, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint, EndpointError


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @get(r'/api/iptables/which')
    @endpoint(api=True)
    def handle_api_get_which_iptables(self, http_context):
        try:
            self.iptables = subprocess.check_output(['which', 'iptables']).decode().strip()
        except subprocess.CalledProcessError as e:
            raise EndpointError(_('Iptables is not installed on this host'))

    @get(r'/api/iptables')
    @endpoint(api=True)
    def handle_api_get_iptables(self, http_context):
        chains_list = subprocess.check_output(f"{self.iptables} -L -n --line-numbers".split()).decode()
        chains = {}

        valid_rule = False
        for line in chains_list.split('\n'):
            if line.startswith("num"):
                valid_rule = True
                continue

            if line in ['\n','']:
                valid_rule = False
                continue

            if line.startswith('Chain'):
                chain = line.split()[1]
                chains[chain] = []
                continue

            if valid_rule:
                details = line.split()
                chains[chain].append({
                    'number': details[0],
                    'target': details[1],
                    'protocol': details[2],
                    'ip_options': details[3],
                    'source': details[4],
                    'destination': details[5],
                    'options': ' '.join(details[6:]),
                })

        return chains

    @post(r'/api/iptables')
    @endpoint(api=True)
    def handle_api_post_iptables(self, http_context):
        pass
