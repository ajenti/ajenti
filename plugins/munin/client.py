from BeautifulSoup import BeautifulSoup
import urllib

from ajenti.com import Plugin


class MuninClient (Plugin):
    icon = '/dl/munin/icon.png'

    def __init__(self):
        self.reset()

    @property
    def domains(self):
        if self._domains is None:
            s = self._fetch(self.config.url)
            ds = s.findAll('span', 'domain')
            self._domains = []
            for d in ds:
                domain = MuninDomain()
                domain.name = d.a.string
                hs = d.parent.findAll('span', 'host')
                for h in hs:
                    host = MuninHost(self)
                    host.name = h.a.string
                    host.domain = domain
                    domain.hosts.append(host)
                self._domains.append(domain)
        return self._domains

    def reset(self):
        self._domains = None

    @property
    def config(self):
        return self.app.get_config(self)

    def _fetch(self, url):
        urllib._urlopener = self._URLOpener(self)
        return BeautifulSoup(urllib.urlopen(url))

    class _URLOpener(urllib.FancyURLopener):
        def __init__(self, client):
            urllib.FancyURLopener.__init__(self)
            self.client = client

        def prompt_user_passwd(self, host, realm):
            return (self.client.config.username, self.client.config.password)


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
            s = self._client._fetch(self._client.config.url + '/%s/%s/'%(self.domain.name, self.name))
            gs = [x.a for x in s.findAll('div', 'lighttext')]
            self._graphs = []
            for g in gs:
                graph = MuninGraph()
                graph.name = g['href'].split('/')[0] if '/' in g['href'] else g['href'].split('.')[0]
                graph.full_name = g.string
                graph.host = self
                graph.url = self._client.config.url + '/%s/%s/%s-day.png'%(self.domain.name, self.name, graph.name)
                self._graphs.append(graph)
        return self._graphs


class MuninGraph:
    def __init__(self):
        self.name = ''
        self.full_name = ''
        self.url = ''

    def history(self, period):
        return self.host._client.config.url + '/%s/%s/%s-%s.png'%(
            self.host.domain.name, self.host.name, self.name, period)
