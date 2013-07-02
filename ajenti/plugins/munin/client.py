from ajenti.api import *

from BeautifulSoup import BeautifulSoup
import requests


@plugin
class MuninClient (BasePlugin):
    default_classconfig = {
        'username': 'username',
        'password': '123',
        'prefix': 'http://localhost:8080/munin'
    }

    classconfig_root = True

    def init(self):
        self.reset()

    def fetch_domains(self):
        self._domains = []
        s = self._fetch('/')
        ds = s.findAll('span', 'domain')
        for d in ds:
            domain = MuninDomain()
            domain.name = str(d.a.string)
            hs = d.parent.findAll('span', 'host')
            for h in hs:
                host = MuninHost(self)
                host.name = str(h.a.string)
                host.domain = domain
                domain.hosts.append(host)
            self._domains.append(domain)

    @property
    def domains(self):
        if self._domains is None:
            self.fetch_domains()
        return self._domains

    def reset(self):
        self._domains = None

    def _fetch(self, url):
        req = requests.get(
            self.classconfig['prefix'] + url,
            auth=(self.classconfig['username'], self.classconfig['password']),
            verify=False,
        )
        if req.status_code == 401:
            raise Exception('auth')
        return BeautifulSoup(req.text)


class MuninDomain:
    def __init__(self):
        self.name = ''
        self.hosts = []


class MuninHost:
    def __init__(self, client):
        self.name = ''
        self._client = client
        self._graphs = None

    @property
    def graphs(self):
        if self._graphs is None:
            s = self._client._fetch('/%s/%s/' % (self.domain.name, self.name))
            gs = [x.a for x in s.findAll('div', 'lighttext')]
            new_content = s.findAll('div', id='content')
            if new_content:
                gs += new_content[0].findAll('a')

            self._graphs = []
            have_graphs = []
            for g in gs:
                graph = MuninGraph()
                graph.name = g['href'].split('/')[0] if '/' in g['href'] else g['href'].split('.')[0]
                graph.full_name = str(g.string or g.img['alt'])
                graph.host = self
                graph.url = '/%s/%s/%s-' % (self.domain.name, self.name, graph.name)
                if not graph.name in have_graphs:
                    self._graphs.append(graph)
                have_graphs.append(graph.name)
        return self._graphs


class MuninGraph:
    def __init__(self):
        self.name = ''
        self.full_name = ''
        self.url = ''
